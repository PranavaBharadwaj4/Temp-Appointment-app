"""appointment_scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
# from appointments.views import AppointmentViewSet
from rest_framework_social_oauth2.views import TokenVerifyView, TokenRefreshView
from appointments.views import doctor_auth_view, doctor_settings_view, patient_form_view

router = routers.DefaultRouter()
# router.register(r'appointments', AppointmentViewSet)

urlpatterns = [

    path('auth/', include('rest_framework_social_oauth2.urls')),
    path('auth/token-verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('accounts/', include('allauth.urls')),
    # path('accounts/', include('allauth.socialaccount.urls')), path('', include(router.urls)),
    path('doctor-auth/', doctor_auth_view, name='doctor_auth'),
    path('doctor-settings/', doctor_settings_view, name='doctor_settings'),
    path('patient-book-appointment/<int:pk>/', patient_form_view, name='patient_book_appointment'),
    # path('patient-confirm-appointment/<int:pk>/', patient_confirm_appointment_view, name='patient_confirm_appointment'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
