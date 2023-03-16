        
       

# views.py
import os
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.conf import settings
from google.auth.transport.requests import Request
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from .models import Doctor, Patient, AppointmentLink, AppointmentSlot
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialAccount
from datetime import timedelta, timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
import uuid
from rest_framework import viewsets, permissions
from .serializers import DoctorSerializer, PatientSerializer, AppointmentLinkSerializer, AppointmentSlotSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class AppointmentSlotViewSet(viewsets.ModelViewSet):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer


class AppointmentLinkViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentLinkSerializer
    basename = 'appointment-link'
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        hash = self.request.query_params.get('hash', None)
        if hash is not None:
            print('this is the hash in the query string', hash)
            print(AppointmentLink.objects.filter(hash=hash))
            linkObject = AppointmentLink.objects.filter(hash=hash)
            # print(linkObject.get('doctor_name'))
            return AppointmentLink.objects.filter(hash=hash)
        extra_data = SocialAccount.objects.get(user=self.request.user).extra_data
        google_id = extra_data['sub']
        doctor = Doctor.objects.get(google_id=google_id)
        print(AppointmentLink.objects.filter(doctor=doctor))
        return AppointmentLink.objects.filter(doctor=doctor)


def home(request):
    return render( request,"index.html")

@login_required
def doctor_setting(request):
    return HttpResponse("done bro")

def storing_doctor(request):
    print("hiiiii")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
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
        doctor = Doctor(user=request.user, google_id=google_id, email=email, name= name)
    doctor.save()

    return redirect('doctor_settings')


# @login_required
def doctor_auth_view(request):
    
    return render(request, 'index.html')


@csrf_exempt
@login_required
def doctor_settings_view(request):
    print("hiiiii")
    extra_data = SocialAccount.objects.get(user=request.user).extra_data
    google_id = extra_data['sub']
    email = extra_data['email']
    name = extra_data.get('name', '')
    # doctor = Doctor( google_id=google_id, email=email, name= name)
    # print(doctor, "is doctor")
    # doctor.save()
    # print(google_id, email, name)


    # Create or update the corresponding Doctor object in the database
    try:
        doctor = Doctor.objects.get(google_id=google_id)
        doctor.google_id = google_id
        doctor.email = email
        doctor.name = name
    except Doctor.DoesNotExist:
        doctor = Doctor( google_id=google_id, email=email, name= name)
    doctor.save()

    # doctor = Doctor.objects.get(user=request.user)

    if request.method == 'POST':
        # Get the appointment link settings from the form
        
        print(request.POST, "is the method lol")
        time_slots = request.POST.get('timeslots')
        days_valid = int(request.POST.get('days_valid'))
        max_participants = int(request.POST.get('max_participants'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        # Compute the start and end times based on the current date/time
        start_date = date.today()
        print(start_date)
        start_time = datetime.strptime(start_time, '%H:%M').time()
        start_datetime = datetime.combine(start_date, start_time)
        end_date = start_date + timedelta(days=days_valid)
        end_time = datetime.strptime(end_time, '%H:%M').time()
        end_datetime = datetime.combine(end_date, end_time)
        print(max_participants, "m", end_datetime, "d", time_slots, "t")
        print(uuid.uuid1())

        # Save the appointment link settings to the database
        appointment_link_settings = AppointmentLink(
            doctor=doctor,
            doctor_name= name,
            max_participants=max_participants,
            expires_at=end_datetime,
            time_slots= time_slots,
            hash = uuid.uuid1()
        )
        appointment_link_settings.save()
        

        return redirect('doctor_settings')
    
    return render(request, 'index.html')



@csrf_exempt
def patient_form_view(request, pk):
    try:
        # Get the appointment link from the database
        link = AppointmentLink.objects.get(hash=pk)
        print(pk)
        # pass
    except AppointmentLink.DoesNotExist:
        # Display an error message if the link does not exist
        # return render(request, 'patient_form.html', {'error_message': 'Invalid link'})
        return HttpResponse("<h2>Invalid Link</h2>")        

    if request.method == 'POST':
        # Create a new patient object
        patient = Patient.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone_number=request.POST['phone_number']
            )
        start_time = request.POST['start_time']
        start_date = request.POST['date']
        start_time = datetime.strptime(start_time, '%H:%M').time()
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        start_datetime = datetime.combine(start_date, start_time)

        # Create a new appointment slot object
        slot = AppointmentSlot.objects.create(
            link=link,
            patient=patient,
            patient_name = request.POST['name'],
            start_time=start_datetime
        )

        # Authenticate with the Google Calendar API
        
        client_secret_file = 'E:\\Projects\\Django\\Appointments App\\appointment_scheduler\\appointments\\client_secret.json'
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        credentials = flow.run_local_server(port=0)
        with open('credentials.json', 'w') as f:
            f.write(credentials.to_json())

        with open('credentials.json', 'r') as f:
            credentials_json = f.read()

        creds = Credentials.from_authorized_user_info(info=credentials_json)
        

        # Create a new event in the doctor's calendar with the appointment information
        try:
            service = build('calendar', 'v3', credentials=creds)
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
            return render(request, HttpResponse("Nope"), {'error_message': 'Error creating appointment'})

        # Display a confirmation message to the patient
        return render(request, HttpResponse("Done"), {'success_message': 'Appointment scheduled successfully'})

    else:
            # Display the patient appointment form
        return render(request, 'index.html')
        # return render(request, 'patient_form.html')



