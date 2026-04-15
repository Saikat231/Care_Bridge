from django.contrib import admin

from .models import Hospital, Profile


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address')
    search_fields = ('name', 'city', 'address')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'hospital', 'specialization', 'phone')
    search_fields = ('user__username', 'user__email', 'specialization', 'hospital__name')
