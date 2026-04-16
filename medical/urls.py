from django.urls import path

from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('add/<int:appointment_id>/', views.add_report, name='add_report'),
    path('update/<int:report_id>/', views.update_report, name='update_report'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
]
