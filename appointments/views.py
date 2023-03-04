# from django.shortcuts import render
# # appointments/views.py

# from datetime import datetime, timedelta
# from django.shortcuts import get_object_or_404
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from google.oauth2.credentials import Credentials
# from googleapiclient.errors import HttpError
# from googleapiclient.discovery import build
# from .models import Appointment, AppointmentSlot
# from .serializers import AppointmentSerializer, AppointmentSlotSerializer
# from .permissions import IsOwnerOrReadOnly
# from appointment_scheduler.settings import GOOGLE_CALENDAR_API_CLIENT_SECRETS_FILE, GOOGLE_CALENDAR_API_SCOPES

# class AppointmentViewSet(viewsets.ModelViewSet):
#     queryset = Appointment.objects.all()
#     serializer_class = AppointmentSerializer
#     permission_classes = [IsOwnerOrReadOnly]

#     # appointments/views.py

# # ...continued from previous step

#     def perform_create(self, serializer):
#         # set the doctor as the current user
#         serializer.save(doctor=self.request.user)

#     @action(detail=True, methods=['post'])
#     def send_link(self, request, pk=None):
#         appointment = self.get_object()
#         # check if the current user is the doctor who created the appointment
#         if appointment.doctor != request.user:
#             return Response({'error': 'You are not authorized to send this link'}, status=status.HTTP_401_UNAUTHORIZED)
#         # get the appointment parameters
#         max_participants = appointment.max_participants
#         expiry_date = appointment.expiry_date
#         # check if the appointment link is expired
#         if expiry_date < datetime.now():
#             return Response({'error': 'This link is no longer active'}, status=status.HTTP_400_BAD_REQUEST)
#         # create a new appointment slot
#         slot_serializer = AppointmentSlotSerializer(data=request.data)
#         if not slot_serializer.is_valid():
#             return Response(slot_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         slot = slot_serializer.save(appointment=appointment)
#         # generate the link for the appointment slot
#         link = f'https://example.com/appointment/{slot.id}/'
#         # send the link to the patient via email or SMS (not implemented)
#         # create a Google Calendar event for the appointment slot
       
        
#         # return the appointment slot details
#         return Response(slot_serializer.data, status=status.HTTP_201_CREATED)

        
       

# views.py

from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from .models import Doctor, Patient, AppointmentLink, AppointmentSlot
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialAccount
from .models import Doctor, AppointmentLink
from datetime import timedelta, timezone
from django.http import HttpResponse

@login_required
def doctor_setting(request):
    return HttpResponse("done bro")

@login_required
def doctor_auth_view(request):
    if request.method == 'POST':
        # Get the authorization code from the form data
        code = request.POST.get('code')

        # Exchange the authorization code for an access token
        adapter = GoogleOAuth2Adapter()
        provider = adapter.get_provider(request)
        access_token = provider.get_access_token(request, code)

        # Use the access token to get the user's Google account information
        account = SocialAccount.objects.get(provider='google', user=request.user)
        extra_data = account.extra_data
        google_id = extra_data['sub']
        email = extra_data['email']
        name = extra_data.get('name', '')

        # Create or update the corresponding Doctor object in the database
        try:
            doctor = Doctor.objects.get(user=request.user)
            doctor.google_id = google_id
            doctor.email = email
            doctor.name = name
        except Doctor.DoesNotExist:
            doctor = Doctor(user=request.user, google_id=google_id, email=email)
        doctor.save()

        return redirect('doctor_settings')
    else:
        # Redirect the doctor to Google's authentication page
        adapter = GoogleOAuth2Adapter()
        provider = adapter.get_provider(request)
        authorize_url = provider.get_auth_url(request)
        return redirect(authorize_url)


@login_required
def doctor_settings_view(request):
    doctor = Doctor.objects.get(user=request.user)

    if request.method == 'POST':
        # Get the appointment link settings from the form
        time_slots = request.POST.get('timeslots')
        days_valid = int(request.POST.get('days_valid'))
        max_participants = int(request.POST.get('max_participants'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        # Compute the start and end times based on the current date/time
        now = timezone.now()
        start_date = now.date()
        start_time = datetime.strptime(start_time, '%H:%M').time()
        start_datetime = datetime.combine(start_date, start_time)
        end_date = start_date + timedelta(days=days_valid)
        end_time = datetime.strptime(end_time, '%H:%M').time()
        end_datetime = datetime.combine(end_date, end_time)

        # Save the appointment link settings to the database
        appointment_link_settings = AppointmentLink(
            doctor=doctor,
            
            max_participants=max_participants,
            expires_at=end_datetime,
            time_slots= time_slots
        )
        appointment_link_settings.save()

        return redirect('doctor_settings')
    else:
        # Display the appointment link settings form
        return render(request, 'doctor_settings.html')


# @login_required
# def appointment_link_view(request):
#     # Generate a unique link for the doctor's appointment
#     link = AppointmentLink.objects.create(doctor=request.user.doctor)

#     # Set the link expiration time
#     expiration_time = datetime.now() + timedelta(days=link.expiration_days)
#     link.expiration_time = expiration_time
#     link.save()

#     # Display the link to the doctor
#     return render(request, 'appointment_link.html', {'link': link})


def patient_form_view(request, link_id):
    try:
        # Get the appointment link from the database
        link = AppointmentLink.objects.get(id=link_id)
    except AppointmentLink.DoesNotExist:
        # Display an error message if the link does not exist
        return render(request, 'patient_form.html', {'error_message': 'Invalid link'})

    if request.method == 'POST':
        # Create a new patient object
        patient = Patient.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone_number=request.POST['phone_number']
            )

        # Create a new appointment slot object
        slot = AppointmentSlot.objects.create(
            link=link,
            patient=patient,
            start_time=request.POST['start_time']
        )

        # Authenticate with the Google Calendar API
        credentials = Credentials.from_authorized_user_info(request.user.doctor.token)

        # Create a new event in the doctor's calendar with the appointment information
        try:
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': 'Appointment with {}'.format(patient.name),
                'location': 'Online',
                'description': 'Appointment with {} on {}'.format(patient.name, slot.start_time.strftime('%m/%d/%Y %I:%M %p')),
                'start': {
                    'dateTime': slot.start_time.isoformat(),
                    'timeZone': settings.TIME_ZONE,
                },
                'end': {
                    'dateTime': (slot.start_time + timedelta(minutes=30)).isoformat(),
                    'timeZone': settings.TIME_ZONE,
                },
                'reminders': {
                    'useDefault': True,
                },
                'conferenceData': {
                    'createRequest': {
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        },
                        'status': {
                            'statusCode': 'success'
                        }
                    }
                }
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            slot.event_id = event['id']
            slot.save()
        except HttpError:
            # Display an error message if there was a problem creating the event
            return render(request, 'patient_form.html', {'error_message': 'Error creating appointment'})

        # Display a confirmation message to the patient
        return render(request, 'patient_form.html', {'success_message': 'Appointment scheduled successfully'})

    else:
            # Display the patient appointment form
        return render(request, 'patient_form.html')



