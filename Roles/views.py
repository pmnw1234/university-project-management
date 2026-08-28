from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SupervisorRequest
from .forms import SupervisorRequestForm, SupervisorAccountCreateForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.views.decorators.cache import never_cache
import logging
from django.db.models import Count, Q
from dashboard.models import Profile
logger = logging.getLogger(__name__)

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

@login_required
def admin_dashboard(request):
    # Restrict access to superusers or staff only
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    # Get counts
    total_users = User.objects.count()
    total_students = User.objects.filter(profile__role='student').count()
    total_supervisors = User.objects.filter(profile__role='supervisor').count()
    total_projects = 0  # Replace with your Project model count
    
    # Count unique departments from profiles (excluding null and empty)
    total_departments = Profile.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values('department').distinct().count()
    
    # Get department list for the chart
    dept_data = Profile.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values('department').annotate(count=Count('id'))
    
    dept_labels = [item['department'] for item in dept_data]
    dept_counts = [item['count'] for item in dept_data]
    
    # Recent users (last 5)
    recent_users = User.objects.all().select_related('profile').order_by('-date_joined')[:5]
    
    # Recent logs
    recent_logs = SupervisorRequest.objects.all().order_by('-created_at')[:3]
    
    # Project status data (replace with actual data)
    in_progress = 0
    pending_review = 0
    completed = 0
    at_risk = 0
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_supervisors': total_supervisors,
        'total_projects': total_projects,
        'total_departments': total_departments,
        'recent_users': recent_users,
        'recent_logs': recent_logs,
        'in_progress': in_progress,
        'pending_review': pending_review,
        'completed': completed,
        'at_risk': at_risk,
        'dept_labels': dept_labels if dept_labels else ['No Departments'],
        'dept_data': dept_counts if dept_counts else [0],
    }
    
    return render(request, 'Admindashboard.html', context)

@login_required
def admin_profile(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    context = {
        'admin_user': request.user,
    }
    return render(request, 'admin_profile.html', context)

@login_required
def admin_users(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    context = {
        'users': users,
        'total_users': users.count(),
    }
    return render(request, 'admin_users.html', context)

@login_required
def admin_projects(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    context = {
        'projects': [],  # Replace with your Project model
    }
    return render(request, 'admin_projects.html', context)

@login_required
def admin_departments(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    # Get all unique departments with counts
    departments_list = []
    dept_names = Profile.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values('department').distinct()
    
    for dept in dept_names:
        dept_name = dept['department']
        departments_list.append({
            'name': dept_name,
            'supervisor_count': Profile.objects.filter(department=dept_name, role='supervisor').count(),
            'student_count': Profile.objects.filter(department=dept_name, role='student').count(),
            'total_count': Profile.objects.filter(department=dept_name).count(),
        })
    
    # Sort by department name
    departments_list.sort(key=lambda x: x['name'])
    
    context = {
        'departments': departments_list,
        'total_departments': len(departments_list),
    }
    return render(request, 'admin_departments.html', context)

@login_required
def admin_supervisors(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    supervisors = User.objects.filter(profile__role='supervisor').select_related('profile')
    context = {
        'supervisors': supervisors,
        'total_supervisors': supervisors.count(),
    }
    return render(request, 'admin_supervisors.html', context)

@login_required
def admin_reports(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    context = {}
    return render(request, 'admin_reports.html', context)

@login_required
def admin_settings(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
    
    context = {}
    return render(request, 'admin_settings.html', context)

@never_cache
@login_required
def system_logs(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('login')

    # All supervisor requests
    logs = (
        SupervisorRequest.objects
        .select_related('user')
        .all()
        .order_by('-created_at')
    )

    # Only pending requests
    pending_logs = (
        SupervisorRequest.objects
        .select_related('user')
        .filter(status='PENDING')
        .order_by('-created_at')
    )

    print("\n" + "=" * 60)
    print("📊 SYSTEM LOGS PAGE LOADED")
    print(f"  Total records: {logs.count()}")
    print(f"  Pending records: {pending_logs.count()}")

    print("\n  All records:")
    for log in logs:
        if log.user:
            username = log.user.username
            first_name = log.user.first_name
            last_name = log.user.last_name
        else:
            username = "NO USER"
            first_name = ""
            last_name = ""

        print(
            f"    ID:{log.pk} | "
            f"Username:{username} | "
            f"Name:{first_name} {last_name} | "
            f"{log.email} | "
            f"{log.status}"
        )
    print("=" * 60 + "\n")

    return render(
        request,
        'system_logs.html',
        {
            'logs': logs,
            'pending_logs': pending_logs,
            'pending_count': pending_logs.count(),
        }
    )

@login_required
def approve_supervisor_request(request, request_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('login')

    sup_req = get_object_or_404(SupervisorRequest, id=request_id)
    
    if sup_req.status != 'PENDING':
        messages.warning(request, f"This request has already been {sup_req.status.lower()}.")
        return redirect('system_logs')
    
    sup_req.status = 'APPROVED'
    sup_req.save()

    user = User.objects.filter(email=sup_req.email).first()
    if user:
        user.is_active = True
        user.save()
        messages.success(request, f"Supervisor account ({user.username}) has been approved and activated.")
    else:
        messages.warning(request, f"Request approved, but no user account found with email {sup_req.email}.")

    return redirect('system_logs')

@login_required
def reject_supervisor_request(request, request_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("login")

    sup_req = get_object_or_404(
        SupervisorRequest,
        id=request_id
    )

    if sup_req.status != "PENDING":
        messages.warning(
            request,
            f"This request has already been {sup_req.status.lower()}."
        )
        return redirect("system_logs")

    sup_req.status = "REJECTED"
    sup_req.save()

    user = sup_req.user
    if user:
        user.is_active = False
        user.save()
        messages.warning(
            request,
            f"Supervisor request for {user.username} was rejected."
        )
    else:
        messages.warning(
            request,
            "Request rejected, but no user account was found."
        )

    return redirect("system_logs")