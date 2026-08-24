from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # CHANGE THIS - Use supervisor_request as the registration URL
    path('admin-panel/system-logs/', views.system_logs, name='system_logs'),
    path('admin-panel/approve/<int:request_id>/', views.approve_supervisor_request, name='approve_supervisor_request'),
    path('admin-panel/reject/<int:request_id>/', views.reject_supervisor_request, name='reject_supervisor_request'),
]