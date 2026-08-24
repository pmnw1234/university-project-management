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

logger = logging.getLogger(__name__)

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

@login_required
def admin_dashboard(request):
    # Restrict access to superusers or staff only
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')
        
    return render(request, 'Admindashboard.html')

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

    # Reject request
    sup_req.status = "REJECTED"
    sup_req.save()

    # Keep account inactive
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