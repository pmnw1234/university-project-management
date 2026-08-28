from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # CHANGE THIS - Use supervisor_request as the registration URL
    path('admin-panel/system-logs/', views.system_logs, name='system_logs'),
    path('admin-panel/approve/<int:request_id>/', views.approve_supervisor_request, name='approve_supervisor_request'),
    path('admin-panel/reject/<int:request_id>/', views.reject_supervisor_request, name='reject_supervisor_request'),
    # Admin URLs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/projects/', views.admin_projects, name='admin_projects'),
    path('admin/departments/', views.admin_departments, name='admin_departments'),
    path('admin/supervisors/', views.admin_supervisors, name='admin_supervisors'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/profile/', views.admin_profile, name='admin_profile'),

]