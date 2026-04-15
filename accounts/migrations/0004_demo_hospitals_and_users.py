from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_demo_hospitals_and_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    Hospital = apps.get_model('accounts', 'Hospital')

    enam, _ = Hospital.objects.get_or_create(
        name='Enam Medical',
        defaults={
            'address': 'Mirpur, Dhaka',
            'city': 'Dhaka',
            'description': 'Enam Medical is a trusted healthcare partner in Dhaka.',
        }
    )

    dhaka_clinic, _ = Hospital.objects.get_or_create(
        name='Dhaka Clinic',
        defaults={
            'address': 'Dhanmondi, Dhaka',
            'city': 'Dhaka',
            'description': 'Dhaka Clinic is a modern facility offering specialist care.',
        }
    )

    doctors = [
        ('saikat', 'Saikat', enam, 'Cardiology'),
        ('shuvo', 'Shuvo', enam, 'General Practice'),
        ('jubu', 'Jubu', dhaka_clinic, 'Orthopedics'),
        ('sanim', 'Sanim', dhaka_clinic, 'Dermatology'),
        ('israful', 'Israful', enam, 'Pediatrics'),
    ]

    patients = [
        ('nafi', 'Nafi', enam),
        ('eusha', 'Eusha', enam),
        ('jeba', 'Jeba', dhaka_clinic),
        ('asha', 'Asha', dhaka_clinic),
    ]

    for username, first_name, hospital, specialization in doctors:
        user, created = User.objects.get_or_create(username=username, defaults={
            'first_name': first_name,
            'email': f'{username}@example.com',
            'password': make_password('password123'),
        })
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = 'doctor'
        profile.specialization = specialization
        profile.hospital = hospital
        profile.save()

    for username, first_name, hospital in patients:
        user, created = User.objects.get_or_create(username=username, defaults={
            'first_name': first_name,
            'email': f'{username}@example.com',
            'password': make_password('password123'),
        })
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = 'patient'
        profile.hospital = hospital
        profile.save()


def reverse_demo_hospitals_and_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Hospital = apps.get_model('accounts', 'Hospital')

    usernames = ['saikat', 'shuvo', 'jubu', 'sanim', 'israful', 'nafi', 'eusha', 'jeba', 'asha']
    User.objects.filter(username__in=usernames).delete()
    Hospital.objects.filter(name__in=['Enam Medical', 'Dhaka Clinic']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_hospital_profile_hospital'),
    ]

    operations = [
        migrations.RunPython(create_demo_hospitals_and_users, reverse_demo_hospitals_and_users),
    ]
