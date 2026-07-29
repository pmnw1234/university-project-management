from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Project, Task, Milestone, ActivityLog
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def dashboard_view(request):
    # Fetch all projects the logged-in user belongs to
    user_projects = request.user.projects.all()
    
    # Check if user selected a project from the dropdown selection box
    selected_project_id = request.GET.get('project_id')
    
    if selected_project_id:
        active_project = get_object_or_404(request.user.projects, id=selected_project_id)
    else:
        active_project = user_projects.first()

    # Base context defaults if no projects exist yet
    context = {
        'user_projects': user_projects,
        'active_project': active_project,
    }

    if active_project:
        # Calculate dynamic task numbers
        tasks = active_project.tasks.all()
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress_tasks = tasks.filter(status='in_progress').count()
        todo_tasks = tasks.filter(status='todo').count()
        
        # Safe breakdown math variables
        progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        # Deadlines and timelines
        upcoming_deadlines = tasks.filter(status='todo', due_date__gte=timezone.now().date()).order_date_by('due_date')[:5]
        milestones = active_project.milestones.all()
        activities = active_project.activities.all()[:5]
        team_members = active_project.members.all()

        # Build dynamic statistics objects out for context variables
        context.update({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks,
            'progress_percentage': progress_percentage,
            'upcoming_deadlines': upcoming_deadlines,
            'milestones': milestones,
            'activities': activities,
            'team_members': team_members,
        })

    return render(request, 'dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_value_valid() if hasattr(form, 'is_value_valid') else form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            raw_role = form.cleaned_data['role']
            
            Profile.objects.create(
                user=user,
                role=raw_role,
                student_id=form.cleaned_data['student_id'] if raw_role.lower() == 'student' else None
            )
            
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    user_role = user.profile.role.lower()
                    if user_role == 'supervisor':
                        return redirect('supervisor_dashboard')
                    elif user_role == 'student':
                        return redirect('dashboard')
                    elif user_role == 'admin':
                        return redirect('admin_dashboard')
                except:
                    pass
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
# Create your views here.
def admin_dashboard_view(request):
    return render(request, 'Admindashboard.html')
