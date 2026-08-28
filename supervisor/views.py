from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from dashboard.models import Project, Profile
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
def supervisor_proposal(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        return redirect('dashboard')
    
    context = {
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'proposals': [],  # Replace with actual proposals
    }
    return render(request, 'supervisor_proposal.html', context)

@login_required
def supervisor_edit_profile(request):
    # Check if user is a supervisor
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'supervisor':
        messages.error(request, "Access denied. You are not a supervisor.")
        return redirect('dashboard')
    
    # Get or create profile
    profile_instance, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = SupervisorProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)

        print("=" * 50)
        print("REQUEST.FILES:", request.FILES)
        print("REQUEST.POST:", request.POST)
        print("=" * 50)

        if u_form.is_valid() and p_form.is_valid():
            # Save user
            u_form.save()
            
            # Manual save for profile with image
            profile = p_form.save(commit=False)
            
            # Handle image separately
            if 'image' in request.FILES and request.FILES['image']:
                profile.image = request.FILES['image']
            
            profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('supervisor_edit_profile')
        else:
            print("User Form Errors:", u_form.errors)
            print("Profile Form Errors:", p_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = SupervisorProfileUpdateForm(instance=profile_instance)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'supervisor_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'profile': profile_instance,
    }
    return render(request, 'supervisor_edit_profile.html', context)