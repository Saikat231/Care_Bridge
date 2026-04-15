from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Profile
from medical.models import MedicalReport
from .forms import AppointmentBookingForm, ReviewForm, DoctorEditForm, NotificationForm
from .models import Appointment, Notification, Review


def _get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def _notify(user, message):
    Notification.objects.create(user=user, message=message)


@login_required
def doctor_list(request):
    query = request.GET.get('q', '')
    doctors = User.objects.filter(profile__role='doctor').order_by('first_name', 'last_name')
    if query:
        doctors = doctors.filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(profile__specialization__icontains=query)
        )
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors, 'query': query})


@login_required
def edit_doctor(request, doctor_id):
    profile = _get_profile(request.user)
    if not (request.user.is_staff or profile.role == 'doctor'):
        messages.error(request, 'Only admins and doctors can edit doctors.')
        return redirect('doctor_list')

    doctor = get_object_or_404(User, pk=doctor_id, profile__role='doctor')
    form = DoctorEditForm(request.POST or None, instance=doctor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Doctor profile updated successfully.')
        return redirect('doctor_list')

    return render(request, 'appointments/edit_doctor.html', {'form': form, 'doctor': doctor})


@login_required
def delete_doctor(request, doctor_id):
    profile = _get_profile(request.user)
    if not (request.user.is_staff or profile.role == 'doctor'):
        messages.error(request, 'Only admins and doctors can delete doctors.')
        return redirect('doctor_list')

    doctor = get_object_or_404(User, pk=doctor_id, profile__role='doctor')
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor deleted successfully.')
        return redirect('doctor_list')

    return render(request, 'appointments/delete_doctor.html', {'doctor': doctor})


@login_required
def book_appointment(request, doctor_id):
    profile = _get_profile(request.user)
    if profile.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('dashboard')

    doctor = get_object_or_404(User, pk=doctor_id, profile__role='doctor')
    form = AppointmentBookingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = request.user
        appointment.doctor = doctor
        appointment.save()
        _notify(doctor, f'New appointment request from {request.user.get_full_name() or request.user.username}.')
        messages.success(request, 'Appointment request sent. The doctor will review it and confirm a scheduled time.')
        return redirect('my_appointments')

    return render(request, 'appointments/book_appointment.html', {'form': form, 'doctor': doctor})


@login_required
def submit_review(request, doctor_id):
    profile = _get_profile(request.user)
    if profile.role != 'patient':
        messages.error(request, 'Only patients can leave reviews.')
        return redirect('dashboard')

    doctor = get_object_or_404(User, pk=doctor_id, profile__role='doctor')
    review = Review.objects.filter(patient=request.user, doctor=doctor).first()
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == 'POST' and form.is_valid():
        new_review = form.save(commit=False)
        new_review.patient = request.user
        new_review.doctor = doctor
        new_review.hospital = doctor.profile.hospital
        new_review.save()
        messages.success(request, 'Thank you! Your review was submitted.')
        return redirect('doctor_list')

    return render(request, 'appointments/submit_review.html', {'form': form, 'doctor': doctor})


@login_required
def my_appointments(request):
    profile = _get_profile(request.user)
    selected_status = request.GET.get('status', 'all')
    status_options = [
        ('all', 'All'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    status_labels = {
        'pending': 'Pending appointment requests',
        'confirmed': 'Confirmed appointments',
        'completed': 'Completed appointment requests',
        'cancelled': 'Cancelled appointment requests',
    }

    if profile.role == 'doctor':
        user_appointments = request.user.appointments_doctor
    elif profile.role == 'admin':
        user_appointments = Appointment.objects.all()
    else:
        user_appointments = request.user.appointments
    pending_appointments = user_appointments.none()
    scheduled_appointments = user_appointments.none()
    other_appointments = user_appointments.none()

    if selected_status != 'all':
        appointments = user_appointments.filter(status=selected_status).order_by(
            'scheduled_at' if selected_status == 'confirmed' else '-created_at'
        )
        return render(request, 'appointments/appointments.html', {
            'profile': profile,
            'appointments': appointments,
            'status_options': status_options,
            'selected_status': selected_status,
            'status_heading': status_labels.get(selected_status, f'{selected_status.title()} appointments'),
            'pending_appointments': pending_appointments,
            'scheduled_appointments': scheduled_appointments,
            'other_appointments': other_appointments,
        })

    pending_appointments = user_appointments.filter(status='pending').order_by('created_at')
    scheduled_appointments = user_appointments.filter(status='confirmed').order_by('scheduled_at')
    other_appointments = user_appointments.exclude(status__in=['pending', 'confirmed']).order_by('-created_at')

    return render(request, 'appointments/appointments.html', {
        'profile': profile,
        'pending_appointments': pending_appointments,
        'scheduled_appointments': scheduled_appointments,
        'other_appointments': other_appointments,
        'status_options': status_options,
        'selected_status': selected_status,
    })


@login_required
def patient_queue(request):
    profile = _get_profile(request.user)
    if profile.role != 'patient':
        messages.error(request, 'Only patients can view the queue.')
        return redirect('dashboard')

    queue = request.user.appointments.filter(status='confirmed', scheduled_at__gte=timezone.now()).order_by('scheduled_at')
    return render(request, 'appointments/queue.html', {'queue': queue, 'profile': profile})


@login_required
def hospital_queue(request):
    profile = _get_profile(request.user)
    if profile.role != 'hospital':
        messages.error(request, 'Only hospital admins can view the hospital queue.')
        return redirect('dashboard')

    appointments = Appointment.objects.filter(hospital=profile.hospital, status='confirmed').order_by('scheduled_at')
    return render(request, 'appointments/hospital_queue.html', {'appointments': appointments, 'profile': profile})


@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user)
    if appointment.status != 'pending':
        messages.error(request, 'This appointment is already confirmed.')
        return redirect('my_appointments')
    
    from .forms import ConfirmAppointmentForm
    form = ConfirmAppointmentForm(request.POST or None, instance=appointment)
    
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.status = 'confirmed'
        appointment.hospital = request.user.profile.hospital
        appointment.serial_number = Appointment.objects.filter(
            doctor=appointment.doctor,
            status='confirmed',
            scheduled_at__date=appointment.scheduled_at.date(),
            scheduled_at__lte=appointment.scheduled_at,
        ).count() + 1
        appointment.save()
        _notify(appointment.patient, f'Your appointment request has been reviewed and confirmed for {appointment.scheduled_at:%Y-%m-%d %H:%M}. Please visit {appointment.hospital.name if appointment.hospital else "the hospital"} and take serial number {appointment.serial_number}.')
        _notify(request.user, f'Appointment confirmed and serial number {appointment.serial_number} assigned.')
        messages.success(request, 'Appointment confirmed and scheduled. The patient has been notified.')
        return redirect('my_appointments')
    
    return render(request, 'appointments/confirm_appointment.html', {'form': form, 'appointment': appointment})


@login_required
def approve_appointment(request, appointment_id):
    profile = _get_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Only admins can approve appointment requests.')
        return redirect('my_appointments')

    appointment = get_object_or_404(Appointment, pk=appointment_id, status='pending')
    from .forms import ConfirmAppointmentForm
    form = ConfirmAppointmentForm(request.POST or None, instance=appointment)

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.status = 'confirmed'
        appointment.hospital = appointment.doctor.profile.hospital or appointment.hospital
        appointment.serial_number = Appointment.objects.filter(
            doctor=appointment.doctor,
            status='confirmed',
            scheduled_at__date=appointment.scheduled_at.date(),
            scheduled_at__lte=appointment.scheduled_at,
        ).count() + 1
        appointment.save()
        _notify(appointment.patient, f'Your appointment request has been approved and scheduled for {appointment.scheduled_at:%Y-%m-%d %H:%M}. Please visit {appointment.hospital.name if appointment.hospital else "the hospital"} and take serial number {appointment.serial_number}.')
        _notify(appointment.doctor, f'Appointment request from {appointment.patient.get_full_name() or appointment.patient.username} was approved by admin and scheduled for {appointment.scheduled_at:%Y-%m-%d %H:%M}.')
        messages.success(request, 'Appointment request approved and scheduled.')
        return redirect('my_appointments')

    return render(request, 'appointments/approve_appointment.html', {'form': form, 'appointment': appointment})


@login_required
def send_notification(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    profile = _get_profile(request.user)

    if request.user != appointment.patient and request.user != appointment.doctor:
        messages.error(request, 'You do not have permission to send a notification for this appointment.')
        return redirect('my_appointments')

    if profile.role == 'doctor':
        recipient = appointment.patient
        button_label = 'Send notification to patient'
    elif profile.role == 'patient':
        recipient = appointment.doctor
        button_label = 'Send notification to doctor'
    else:
        messages.error(request, 'Only doctors and patients can send notifications.')
        return redirect('my_appointments')

    form = NotificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        notification = form.save(commit=False)
        notification.user = recipient
        notification.message = f'From {request.user.get_full_name() or request.user.username}: {notification.message}'
        notification.save()
        messages.success(request, 'Notification sent successfully.')
        return redirect('my_appointments')

    return render(request, 'appointments/send_notification.html', {
        'form': form,
        'appointment': appointment,
        'recipient': recipient,
        'button_label': button_label,
    })


@login_required
def notification_list(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'appointments/notifications.html', {'notifications': notifications})


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    profile = _get_profile(request.user)
    
    # Check permission: only the doctor or admin can edit appointments
    if request.user != appointment.doctor and not (request.user.is_staff or profile.role == 'admin'):
        messages.error(request, 'You do not have permission to edit this appointment.')
        return redirect('my_appointments')
    
    from .forms import AppointmentEditForm
    form = AppointmentEditForm(request.POST or None, instance=appointment)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        _notify(appointment.patient, f'Your appointment with Dr. {request.user.get_full_name() or request.user.username} has been rescheduled to {appointment.scheduled_at:%Y-%m-%d %H:%M}.')
        _notify(request.user, 'Appointment updated successfully.')
        messages.success(request, 'Appointment updated successfully.')
        return redirect('my_appointments')
    
    return render(request, 'appointments/edit_appointment.html', {'form': form, 'appointment': appointment})


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.user != appointment.patient and request.user != appointment.doctor:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')

    appointment.status = 'cancelled'
    appointment.save()
    _notify(appointment.patient, f'Appointment on {appointment.scheduled_at:%Y-%m-%d %H:%M} was cancelled.')
    _notify(appointment.doctor, f'Appointment on {appointment.scheduled_at:%Y-%m-%d %H:%M} was cancelled.')
    messages.success(request, 'Appointment cancelled.')
    return redirect('my_appointments')


@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    profile = _get_profile(request.user)
    
    # Check permission: only admins can delete appointments
    if not (request.user.is_staff or profile.role == 'admin'):
        messages.error(request, 'You do not have permission to delete this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        appointment_name = f"Appointment for {appointment.patient.username} with {appointment.doctor.username} on {appointment.scheduled_at:%Y-%m-%d %H:%M}"
        appointment.delete()
        messages.success(request, f'Appointment "{appointment_name}" has been deleted.')
        return redirect('my_appointments')
    
    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})


@login_required
def notifications_json(request):
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:10]
    data = [
        {
            'id': notification.id,
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for notification in notifications
    ]
    return JsonResponse({'notifications': data, 'count': notifications.count()})


@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('dashboard')
