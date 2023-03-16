
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from appointments.views import doctor_auth_view, doctor_settings_view, patient_form_view, home, storing_doctor

router = routers.DefaultRouter()


urlpatterns = [
    path('admin/', admin.site.urls), 
    path("doctor-auth/", doctor_auth_view, name='doctor_auth'),
    path('doctor-settings/', doctor_settings_view, name='doctor_settings'),
    path('patient-book-appointment/<str:pk>/', patient_form_view, name='patient_book_appointment'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('accounts/google/login/callback/', storing_doctor),
    path('', include("appointments.urls")),

]
