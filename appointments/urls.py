from django.urls import path

from . import views

urlpatterns = [
    path('', views.my_appointments, name='my_appointments'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/edit/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('doctors/delete/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('review/<int:doctor_id>/', views.submit_review, name='submit_review'),
    path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('send-notification/<int:appointment_id>/', views.send_notification, name='send_notification'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('queue/', views.patient_queue, name='patient_queue'),
    path('hospital-queue/', views.hospital_queue, name='hospital_queue'),
    path('notifications/', views.notifications_json, name='notifications_json'),
    path('notifications/list/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/', views.mark_notifications_read, name='notifications_mark_read'),
]
