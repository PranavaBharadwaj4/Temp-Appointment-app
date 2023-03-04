# appointments/serializers.py

from rest_framework import serializers
from .models import Appointment, AppointmentSlot

class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    slots = AppointmentSlotSerializer(many=True)

    class Meta:
        model = Appointment
        fields = '__all__'
