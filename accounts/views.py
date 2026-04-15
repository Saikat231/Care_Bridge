from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .forms import DoctorCreateForm, HospitalCreateForm, HospitalEditForm, ProfileForm, RegisterForm
from .models import Hospital, Profile
from appointments.models import Appointment
from medical.models import MedicalReport


def _get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        role = form.cleaned_data['role']
        if role == 'admin':
            user.is_staff = True
        user.save()
        profile = Profile.objects.get(user=user)
        profile.role = role
        profile.specialization = form.cleaned_data.get('specialization', '')
        profile.phone = form.cleaned_data.get('phone', '')
        profile.profile_picture = form.cleaned_data.get('profile_picture')
        profile.hospital = form.cleaned_data.get('hospital')
        profile.save()

        messages.success(request, 'Your account was created. Please log in.')
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    profile = _get_profile(request.user)
    context = {
        'profile': profile,
        'unread_notifications': request.user.notifications.filter(is_read=False).count(),
    }

    if profile.role == 'doctor':
        context['appointments'] = request.user.appointments_doctor.order_by('-created_at')[:5]
        context['reports'] = request.user.authored_reports.order_by('-created_at')[:5]
    elif profile.role == 'hospital':
        # Hospital dashboard stats
        context['total_patients'] = Profile.objects.filter(role='patient').count()
        context['total_doctors'] = Profile.objects.filter(role='doctor').count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_reports'] = MedicalReport.objects.count()
        context['recent_appointments'] = Appointment.objects.order_by('-created_at')[:10]
    elif profile.role == 'admin':
        context['total_patients'] = Profile.objects.filter(role='patient').count()
        context['total_doctors'] = Profile.objects.filter(role='doctor').count()
        context['total_hospitals'] = Hospital.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_reports'] = MedicalReport.objects.count()
        context['appointments'] = Appointment.objects.order_by('-created_at')[:10]
        context['reports'] = MedicalReport.objects.order_by('-created_at')[:10]
    else:
        context['appointments'] = request.user.appointments.order_by('-created_at')[:5]
        context['reports'] = request.user.medical_reports.order_by('-created_at')

    return render(request, 'accounts/dashboard.html', context)


@login_required
def hospital_list(request):
    hospitals = Hospital.objects.all().order_by('name')
    return render(request, 'accounts/hospital_list.html', {'hospitals': hospitals})


@login_required
def hospital_detail(request, hospital_id):
    hospital = get_object_or_404(Hospital, pk=hospital_id)
    doctors = Profile.objects.filter(role='doctor', hospital=hospital)
    return render(request, 'accounts/hospital_detail.html', {'hospital': hospital, 'doctors': doctors})


@login_required
def add_doctor(request):
    profile = _get_profile(request.user)
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'Only admins and doctors can add new doctors.')
        return redirect('doctor_list')

    if request.method == 'POST':
        form = DoctorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            doctor_profile = Profile.objects.get(user=user)
            doctor_profile.role = 'doctor'
            doctor_profile.specialization = form.cleaned_data.get('specialization', '')
            doctor_profile.phone = form.cleaned_data.get('phone', '')
            doctor_profile.profile_picture = form.cleaned_data.get('profile_picture')
            doctor_profile.hospital = form.cleaned_data.get('hospital')
            doctor_profile.save()
            messages.success(request, 'New doctor added successfully.')
            return redirect('doctor_list')
    else:
        form = DoctorCreateForm()

    return render(request, 'accounts/add_doctor.html', {'form': form})


@login_required
def add_hospital(request):
    profile = _get_profile(request.user)
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'Only admins and doctors can add new hospitals.')
        return redirect('hospital_list')

    if request.method == 'POST':
        form = HospitalCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New hospital added successfully.')
            return redirect('hospital_list')
    else:
        form = HospitalCreateForm()

    return render(request, 'accounts/add_hospital.html', {'form': form})


@login_required
def edit_profile(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


@login_required
def edit_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, pk=hospital_id)
    profile = _get_profile(request.user)
    
    # Check permission: only staff admins and doctors can edit hospitals
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'You do not have permission to edit this hospital.')
        return redirect('hospital_detail', hospital_id=hospital_id)
    
    if request.method == 'POST':
        from .forms import HospitalEditForm
        form = HospitalEditForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital details have been updated.')
            return redirect('hospital_detail', hospital_id=hospital_id)
    else:
        from .forms import HospitalEditForm
        form = HospitalEditForm(instance=hospital)
    
    return render(request, 'accounts/edit_hospital.html', {'form': form, 'hospital': hospital})


@login_required
def delete_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, pk=hospital_id)
    profile = _get_profile(request.user)
    
    # Check permission: only staff admins and doctors can delete hospitals
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'You do not have permission to delete this hospital.')
        return redirect('hospital_detail', hospital_id=hospital_id)
    
    if request.method == 'POST':
        hospital_name = hospital.name
        hospital.delete()
        messages.success(request, f'Hospital "{hospital_name}" has been deleted.')
        return redirect('hospital_list')
    
    return render(request, 'accounts/delete_hospital.html', {'hospital': hospital})


@login_required
def edit_doctor(request, doctor_id):
    doctor_user = get_object_or_404(User, pk=doctor_id)
    doctor_profile = _get_profile(doctor_user)
    profile = _get_profile(request.user)
    
    # Check permission: only staff admins and doctors can edit doctors
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'You do not have permission to edit this doctor.')
        return redirect('doctor_list')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=doctor_profile, user=doctor_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor details have been updated.')
            return redirect('doctor_list')
    else:
        form = ProfileForm(instance=doctor_profile, user=doctor_user)
    
    return render(request, 'accounts/edit_doctor.html', {'form': form, 'doctor': doctor_user})


@login_required
def delete_doctor(request, doctor_id):
    doctor_user = get_object_or_404(User, pk=doctor_id)
    doctor_profile = _get_profile(doctor_user)
    profile = _get_profile(request.user)
    
    # Check permission: only staff admins and doctors can delete doctors
    if not (request.user.is_staff or profile.role in ['doctor', 'admin']):
        messages.error(request, 'You do not have permission to delete this doctor.')
        return redirect('doctor_list')
    
    if request.method == 'POST':
        doctor_name = doctor_user.get_full_name() or doctor_user.username
        doctor_user.delete()
        messages.success(request, f'Doctor "{doctor_name}" has been deleted.')
        return redirect('doctor_list')
    
    return render(request, 'accounts/delete_doctor.html', {'doctor': doctor_user})
