from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profile
from appointments.models import Appointment
from .forms import MedicalReportForm
from .models import MedicalReport


def _get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def report_list(request):
    profile = _get_profile(request.user)
    if profile.role == 'doctor':
        reports = MedicalReport.objects.filter(doctor=request.user).order_by('-created_at')
    else:
        reports = request.user.medical_reports.order_by('-created_at')

    return render(request, 'medical/reports.html', {'reports': reports, 'profile': profile})


@login_required
def add_report(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user)
    form = MedicalReportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.patient = appointment.patient
        report.doctor = request.user
        report.appointment = appointment
        report.save()
        messages.success(request, 'Medical report added successfully.')
        return redirect('report_list')

    return render(request, 'medical/add_report.html', {'form': form, 'appointment': appointment})


@login_required
def update_report(request, report_id):
    report = get_object_or_404(MedicalReport, pk=report_id, doctor=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(MedicalReport.STATUS_CHOICES):
            report.status = new_status
            report.save()
            messages.success(request, 'Report status updated.')
        return redirect('report_list')

    return render(request, 'medical/update_report.html', {'report': report})


@login_required
def report_detail(request, report_id):
    profile = _get_profile(request.user)
    if profile.role == 'doctor':
        report = get_object_or_404(MedicalReport, pk=report_id, doctor=request.user)
    else:
        report = get_object_or_404(MedicalReport, pk=report_id, patient=request.user)

    return render(request, 'medical/report_detail.html', {'report': report, 'profile': profile})
