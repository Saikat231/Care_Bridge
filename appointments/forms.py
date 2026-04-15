from django import forms
from django.forms import DateTimeInput

from django.contrib.auth.models import User
from .models import Appointment, Review, Notification


class AppointmentBookingForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Appointment date and time'
    )

    class Meta:
        model = Appointment
        fields = ['scheduled_at', 'reason']
        labels = {
            'reason': 'Reason for appointment',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating',
            'comment': 'Your review',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your experience...'}),
        }


class DoctorEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message']
        labels = {
            'message': 'Notification message',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a message to the other user...'}),
        }


class AppointmentEditForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Appointment date and time'
    )

    class Meta:
        model = Appointment
        fields = ['scheduled_at', 'reason']
        labels = {
            'reason': 'Reason for appointment',
        }


class ConfirmAppointmentForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Confirm appointment date and time'
    )

    class Meta:
        model = Appointment
        fields = ['scheduled_at']
