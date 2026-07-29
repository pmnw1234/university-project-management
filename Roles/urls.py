from django.urls import path
from . import views

urlpatterns = [
    path('supervisor/request/', views.supervisor_request, name='supervisor_request'),
    path('supervisor/status/<int:request_id>/', views.supervisor_status, name='supervisor_status'),
    path('admin-panel/system-logs/', views.system_logs, name='system_logs'),
    path('admin-panel/approve/<int:request_id>/', views.approve_supervisor_request, name='approve_supervisor_request'),
    path('admin-panel/reject/<int:request_id>/', views.reject_supervisor_request, name='reject_supervisor_request'),
    path('supervisor/register/<int:request_id>/', views.supervisor_register, name='supervisor_register'),
]