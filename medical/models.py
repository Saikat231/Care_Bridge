from django.contrib.auth.models import User
from django.db import models

from appointments.models import Appointment


class MedicalReport(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finalized', 'Finalized'),
        ('reviewed', 'Reviewed'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_reports')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_reports')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    title = models.CharField(max_length=200)
    details = models.TextField()
    report_image = models.ImageField(upload_to='medical_reports/', blank=True, null=True, help_text='Upload test results, X-rays, or other medical images')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Report for {self.patient.username} by {self.doctor.username if self.doctor else "Unknown"}'
