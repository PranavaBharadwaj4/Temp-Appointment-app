from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser

# Create your models here.
# appointments/models.py

class Doctor(AbstractUser):
    name = models.CharField(max_length=255)
    # email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255)
    

class Patient(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

class AppointmentLink(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    max_participants = models.IntegerField()
    hash = models.CharField(max_length=255)
    time_slots = JSONField()

class AppointmentSlot(models.Model):
    link = models.ForeignKey('AppointmentLink', on_delete=models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    patient_name =models.CharField(max_length=255)
    start_time = models.DateTimeField()
    event_id = models.CharField(max_length=255)




