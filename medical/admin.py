from django.contrib import admin

from .models import MedicalReport


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'doctor', 'created_at')
    search_fields = ('patient__username', 'doctor__username', 'title')
    list_filter = ('doctor',)
