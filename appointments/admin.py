from django.contrib import admin

from .models import Appointment, Notification


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_at', 'status', 'created_at')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__username', 'doctor__username', 'reason')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')
