from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile, User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from .models import Project, Task, Milestone, ActivityLog, Team
=======
from .models import Project, Task, Milestone, ActivityLog
from django.shortcuts import render, redirect, get_object_or_404
>>>>>>> 7ce9afe351e51589e5f5be5eac14bb47bf8fee0b

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
        # ✅ CORRECT
        upcoming_deadlines = tasks.filter(status='todo', due_date__gte=timezone.now().date()).order_by('due_date')[:5]
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

@login_required
def projects(request):

    projects = Project.objects.filter(
        members=request.user
    )

    context = {
        "projects": projects,
    }

    return render(request, "projects.html", context)

@login_required
def create_project(request):
    # Only fetch teams where current user is the leader
    user_led_teams = Team.objects.filter(leader=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        team_id = request.POST.get('team')
        supervisor_username = request.POST.get('supervisor_username', '').strip()

        # 1. Validate Team selection and ensure user is the leader
        try:
            team = Team.objects.get(id=team_id, leader=request.user)
        except Team.DoesNotExist:
            messages.error(request, "Only team leaders can create or submit a project proposal for this team.")
            return render(request, 'create_project.html', {'user_led_teams': user_led_teams})

        # 2. Look up Supervisor by Username
        supervisor = None
        if supervisor_username:
            try:
                supervisor = User.objects.get(username=supervisor_username)
            except User.DoesNotExist:
                messages.error(request, f"Supervisor username '{supervisor_username}' does not exist.")
                return render(request, 'create_project.html', {
                    'user_led_teams': user_led_teams,
                    'name': name,
                    'description': description,
                    'supervisor_username': supervisor_username,
                })

        # 3. Create Project & Add Members
        project = Project.objects.create(
            name=name,
            description=description,
            team=team,
            supervisor=supervisor,
            status='pending'  # Sent as proposal
        )

        # Add leader and all team members to project.members
        project.members.add(team.leader)
        project.members.add(*team.members.all())

        messages.success(request, "Project proposal submitted successfully!")
        return redirect('projects')

    context = {
        'user_led_teams': user_led_teams
    }
    return render(request, 'create_project.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def edit_profile(request):
    profile_instance, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            
            # Change redirect target from 'edit_profile' to 'dashboard'
            return redirect('dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_instance)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'edit_profile.html', context)
# Create your views here.
def admin_dashboard_view(request):
    return render(request, 'Admindashboard.html')
