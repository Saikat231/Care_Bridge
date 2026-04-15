from django.contrib.auth.models import User
from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_doctor')
    hospital = models.ForeignKey('accounts.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    scheduled_at = models.DateTimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    serial_number = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.username} → {self.doctor.username} at {self.scheduled_at:%Y-%m-%d %H:%M}'

    @property
    def queue_display(self):
        return self.serial_number if self.serial_number is not None else 'Pending'


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_reviews')
    hospital = models.ForeignKey('accounts.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.patient.username} for {self.doctor.username} ({self.rating})'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = 'Read' if self.is_read else 'Unread'
        return f'[{status}] {self.user.username}: {self.message}'
