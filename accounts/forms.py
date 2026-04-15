from django import forms
from django.contrib.auth.models import User
from django.forms import HiddenInput

from .models import Hospital, Profile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label='I am a')
    specialization = forms.CharField(required=False, label='Specialization')
    phone = forms.CharField(required=False, label='Phone number')
    profile_picture = forms.ImageField(required=False, label='Profile Picture')
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.none(), required=False, label='Hospital')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hospital'].queryset = Hospital.objects.all()


class DoctorCreateForm(RegisterForm):
    role = forms.CharField(widget=HiddenInput(), initial='doctor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'doctor'
        self.fields['role'].widget = HiddenInput()


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email')
    specialization = forms.CharField(required=False, label='Specialization')
    phone = forms.CharField(required=False, label='Phone number')
    profile_picture = forms.ImageField(required=False, label='Profile Picture')
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False, label='Hospital')

    class Meta:
        model = Profile
        fields = ['specialization', 'phone', 'profile_picture', 'hospital']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        if commit:
            profile.save()
        return profile


class HospitalEditForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'city', 'email', 'phone', 'description', 'banner_image', 'logo']


class HospitalCreateForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'city', 'email', 'phone', 'description', 'banner_image', 'logo']
