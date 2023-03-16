from django.urls import path, include
from rest_framework import routers
from .views import DoctorViewSet, PatientViewSet, AppointmentLinkViewSet, AppointmentSlotViewSet

router = routers.DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'link', AppointmentLinkViewSet,basename='appointment-link')
router.register(r'slots', AppointmentSlotViewSet,basename='appointment-slot')

urlpatterns = [
    path('api/', include(router.urls)),
    # Add other URL patterns here as needed
]
