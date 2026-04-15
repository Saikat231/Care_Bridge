from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('hospitals/add/', views.add_hospital, name='add_hospital'),
    path('hospitals/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('hospitals/<int:hospital_id>/edit/', views.edit_hospital, name='edit_hospital'),
    path('hospitals/<int:hospital_id>/delete/', views.delete_hospital, name='delete_hospital'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:doctor_id>/edit/', views.edit_doctor, name='edit_doctor'),
    path('doctors/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
]
