import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Care_Bridge.settings')
django.setup()

from django.contrib.auth.models import User

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@gmail.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin.set_password('Admin@123')
    admin.save()
    print('✓ Admin user created: admin / Admin@123')
else:
    print('✓ Admin user exists: admin')
print(f'  is_staff: {admin.is_staff}')
