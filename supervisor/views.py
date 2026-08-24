from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from dashboard.models import Project, Profile  # Combined import
from .forms import UserUpdateForm, ProfileUpdateForm, SupervisorProfileUpdateForm

@login_required
def supervisor_dashboard(request):
    # Check if user is a supervisor
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        return redirect('dashboard')
    
    context = {
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'total_projects': 0,
        'in_progress_projects': 0,
        'pending_reviews': 0,
        'completed_projects': 0,
        'at_risk_projects': 0,
        'projects': [],
        'recent_feedback': [],
        'current_month': "August 2026",
    }
    return render(request, 'supervisordashboard.html', context)

@login_required
def supervisor_projects(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        return redirect('dashboard')
    
    context = {
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
    }
    return render(request, 'supervisor_projects.html', context)

@login_required
def supervisor_reviews(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        return redirect('dashboard')
    
    context = {
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
    }
    return render(request, 'supervisor_reviews.html', context)

@login_required
def supervisor_edit_profile(request):
    # Check if user is a supervisor
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        messages.error(request, "Access denied. You are not a supervisor.")
        return redirect('dashboard')
    
    profile_instance = request.user.profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = SupervisorProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('supervisor_edit_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = SupervisorProfileUpdateForm(instance=profile_instance)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
    }
    return render(request, 'supervisor_edit_profile.html', context)