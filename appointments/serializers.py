# appointments/serializers.py

from rest_framework import serializers
from .models import Doctor, Patient, AppointmentLink, AppointmentSlot

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class AppointmentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentLink
        fields = '__all__'

class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = '__all__'