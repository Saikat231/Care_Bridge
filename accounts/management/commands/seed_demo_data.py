import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile
from accounts.models import Hospital, Profile
from appointments.models import Appointment, Review, Notification
from medical.models import MedicalReport
from django.utils import timezone
from datetime import timedelta


def generate_demo_image(name, width=200, height=200):
    """Generate a simple demo image with text."""
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    # Draw a simple circle
    draw.ellipse([10, 10, width-10, height-10], fill=(37, 99, 235), outline=(25, 99, 200), width=3)
    # Add text
    draw.text((width//2 - 20, height//2 - 10), name[:8], fill=(255, 255, 255))
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return ContentFile(img_io.read(), name=f'{name.lower().replace(" ", "_")}.png')


class Command(BaseCommand):
    help = 'Populate demo data for the Care Bridge project'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))

        # Create hospitals
        hospitals = []
        hospital_data = [
            {
                'name': 'Enam Medical Center',
                'address': 'Mirpur, Dhaka',
                'city': 'Dhaka',
                'email': 'info@enammedical.com',
                'phone': '+880-2-55123456',
                'description': 'Leading multi-specialty hospital in Mirpur with advanced diagnostic facilities.'
            },
            {
                'name': 'Dhaka Clinic & Diagnostics',
                'address': 'Dhanmondi, Dhaka',
                'city': 'Dhaka',
                'email': 'contact@dhakaclinic.com',
                'phone': '+880-2-61234567',
                'description': 'Modern diagnostic center with expert specialists in all major disciplines.'
            },
            {
                'name': 'Green Life Hospital',
                'address': 'Gulshan, Dhaka',
                'city': 'Dhaka',
                'email': 'admin@greenlifehospital.com',
                'phone': '+880-2-88888888',
                'description': 'State-of-the-art healthcare facility with 24/7 emergency services.'
            },
            {
                'name': 'Medicare Plus',
                'address': 'Banani, Dhaka',
                'city': 'Dhaka',
                'email': 'support@medicareplus.com',
                'phone': '+880-2-99999999',
                'description': 'Premier healthcare center providing comprehensive medical services.'
            },
        ]

        for h_data in hospital_data:
            hospital, created = Hospital.objects.get_or_create(
                name=h_data['name'],
                defaults={
                    'address': h_data['address'],
                    'city': h_data['city'],
                    'email': h_data['email'],
                    'phone': h_data['phone'],
                    'description': h_data['description'],
                    'banner_image': generate_demo_image(f"Hospital {h_data['name'][:8]}", 400, 200),
                }
            )
            hospitals.append(hospital)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created hospital: {hospital.name}'))

        # Initialize lists
        doctors = []
        patients = []

        # Create doctors
        doctor_data = [
            ('israfil', 'Israfil', 'Islam', 'Israfil@gmail.com', hospitals[0], 'Pediatrics'),
            ('saikat', 'Saikat', 'Khan', 'Saikat@gmail.com', hospitals[0], 'Cardiology'),
            ('jubu', 'Jubu', 'Ahmed', 'Jubu@gmail.com', hospitals[1], 'Orthopedics'),
            ('sanim', 'Sanim', 'Hassan', 'Sanim@gmail.com', hospitals[1], 'Dermatology'),
            ('rifat', 'Rifat', 'Roy', 'Rifat@gmail.com', hospitals[2], 'Neurology'),
            ('maruf', 'Maruf', 'Ali', 'Maruf@gmail.com', hospitals[2], 'Gynecology'),
            ('khalil', 'Khalil', 'Mahmud', 'Khalil@gmail.com', hospitals[3], 'Oncology'),
        ]

        for username, first_name, last_name, email, hospital, specialization in doctor_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': make_password('DoctorPass@123'),
                }
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = 'doctor'
            profile.specialization = specialization
            profile.hospital = hospital
            if not profile.profile_picture:
                profile.profile_picture = generate_demo_image(f"Dr {first_name}")
            profile.phone = '+880-1XXXXXXXXX'
            profile.save()
            doctors.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created doctor: Dr. {first_name} {last_name}'))

        # Create patients
        patient_data = [
            ('jeba', 'Jeba', 'Akter', 'Jeba@gmail.com', hospitals[1]),
        ]

        for username, first_name, last_name, email, hospital in patient_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': make_password('PatientPass@123'),
                }
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = 'patient'
            profile.hospital = hospital
            if not profile.profile_picture:
                profile.profile_picture = generate_demo_image(first_name)
            profile.phone = '+880-1XXXXXXXXX'
            profile.save()
            patients.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created patient: {first_name} {last_name}'))

        # Create appointments
        appointment_count = 0
        for i, patient in enumerate(patients):
            for j in range(2):
                doctor = doctors[(i + j) % len(doctors)]
                scheduled_time = timezone.now() + timedelta(days=(j+1)*3)
                appointment, created = Appointment.objects.get_or_create(
                    patient=patient,
                    doctor=doctor,
                    scheduled_at=scheduled_time,
                    defaults={
                        'reason': f'Regular checkup {j+1}',
                        'status': 'confirmed' if j == 0 else 'pending',
                        'hospital': doctor.profile.hospital,
                    }
                )
                if created:
                    appointment_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {appointment_count} appointments'))

        # Create medical reports
        report_count = 0
        for i, patient in enumerate(patients[:4]):
            doctor = doctors[i % len(doctors)]
            report, created = MedicalReport.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                defaults={
                    'title': f'Health Report - {patient.first_name}',
                    'details': f'Patient {patient.get_full_name()} visited for routine checkup. All vitals are normal. Continue current medications.',
                    'status': 'completed' if i % 2 == 0 else 'draft',
                }
            )
            if created:
                report_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {report_count} medical reports'))

        # Create reviews
        review_count = 0
        ratings = [5, 4, 5, 4, 3, 5, 4, 4]
        comments = [
            'Excellent doctor, very professional and caring.',
            'Great experience, highly recommend.',
            'Very knowledgeable and patient with me.',
            'Good service, will visit again.',
            'Amazing care and support.',
            'Wonderful specialist, cured my issue.',
            'Professional and friendly staff.',
            'Best hospital experience ever.',
        ]
        for i, patient in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            review, created = Review.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                defaults={
                    'rating': ratings[i % len(ratings)],
                    'comment': comments[i % len(comments)],
                    'hospital': doctor.profile.hospital,
                }
            )
            if created:
                review_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {review_count} reviews'))

        # Create notifications
        notification_count = 0
        notification_messages = [
            'Your appointment has been confirmed.',
            'New appointment request from a patient.',
            'Your medical report is ready.',
            'Doctor has replied to your query.',
            'Appointment reminder: Tomorrow at 2 PM',
            'Your prescription has been updated.',
        ]
        for i, patient in enumerate(patients):
            for j in range(2):
                notif, created = Notification.objects.get_or_create(
                    user=patient,
                    message=notification_messages[(i + j) % len(notification_messages)],
                    defaults={'is_read': i % 2 == 0}
                )
                if created:
                    notification_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Created {notification_count} notifications'))

        self.stdout.write(self.style.SUCCESS('\n✓ Demo data successfully created!'))
        self.stdout.write(self.style.WARNING('\nTest Accounts:'))
        self.stdout.write(f'  Doctor: israfil / DoctorPass@123')
        self.stdout.write(f'  Doctor: saikat / DoctorPass@123')
        self.stdout.write(f'  Patient: jeba / PatientPass@123')
        self.stdout.write(f'  Admin: Create via Django admin\n')
