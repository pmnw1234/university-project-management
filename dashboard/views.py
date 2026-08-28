from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile, User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Project, Task, Milestone, ActivityLog, Team, TaskAttachment
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task, Milestone, ActivityLog, Team
from django.shortcuts import render, redirect, get_object_or_404
from Roles.models import SupervisorRequest
from django.db import transaction

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
    if request.method == "POST":
        print("\n" + "=" * 70)
        print("📝 REGISTRATION POST RECEIVED")
        print("POST DATA:")
        print(request.POST)
        print("=" * 70)

        form = RegistrationForm(request.POST)

        print("\nFORM VALID:", form.is_valid())

        if not form.is_valid():
            print("\n❌ FORM ERRORS:")
            print(form.errors)
            print("=" * 70 + "\n")
            messages.error(request, "Registration form is invalid. Please check the fields.")
            return render(request, "register.html", {"form": form})

        print("\n✅ FORM IS VALID")

        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        role = form.cleaned_data["role"].lower()
        student_id = form.cleaned_data.get("student_id")
        staff_id = form.cleaned_data.get("staff_id")
        department = request.POST.get("department", "General")

        print("Username:", username)
        print("Email:", email)
        print("Role:", role)
        print("Student ID:", student_id)
        print("Staff ID:", staff_id)
        print("Department:", department)

        # DUPLICATE USERNAME
        if User.objects.filter(username=username).exists():
            print("❌ USERNAME ALREADY EXISTS")
            messages.error(request, "Username already exists.")
            return render(request, "register.html", {"form": form})

        # DUPLICATE EMAIL
        if User.objects.filter(email=email).exists():
            print("❌ EMAIL ALREADY EXISTS")
            messages.error(request, "Email already exists.")
            return render(request, "register.html", {"form": form})

        try:
            print("\n🔄 STARTING DATABASE TRANSACTION")

            with transaction.atomic():
                # CREATE USER
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                print("✅ USER CREATED")
                print("User ID:", user.id)

                # Supervisor must wait for admin
                if role == "supervisor":
                    user.is_active = False
                    user.save()
                    print("🔒 SUPERVISOR ACCOUNT SET INACTIVE")
                else:
                    user.is_active = True
                    user.save()
                    print("✅ STUDENT ACCOUNT ACTIVE")

                # ----------------------------------------
                # CREATE PROFILE WITH DEPARTMENT
                # ----------------------------------------
                Profile.objects.create(
                    user=user,
                    role=role,
                    student_id=student_id if role == "student" else None,
                    staff_id=staff_id if role == "supervisor" else None,
                    department=department if role == "supervisor" else None,  # FIX: Add department to Profile
                )
                print("✅ PROFILE CREATED WITH DEPARTMENT:", department if role == "supervisor" else "N/A")

                # SUPERVISOR REQUEST
                if role == "supervisor":
                    supervisor_request = SupervisorRequest.objects.create(
                        user=user,
                        first_name="",
                        last_name="",
                        email=email,
                        department=department,
                        status="PENDING",
                    )
                    print("✅ SUPERVISOR REQUEST CREATED")
                    print("Request ID:", supervisor_request.id)
                    print("Request Status:", supervisor_request.status)

                    messages.success(
                        request,
                        "Registration submitted successfully. Your supervisor account is waiting for admin approval."
                    )
                else:
                    messages.success(
                        request,
                        "Student account created successfully."
                    )

            print("\n✅ TRANSACTION COMPLETED SUCCESSFULLY")
            print("➡️ REDIRECTING TO LOGIN")
            print("=" * 70 + "\n")
            return redirect("login")

        except Exception as e:
            print("\n" + "=" * 70)
            print("❌ REGISTRATION EXCEPTION")
            print("ERROR TYPE:", type(e).__name__)
            print("ERROR:", str(e))
            print("=" * 70 + "\n")
            messages.error(request, f"Registration failed: {e}")
            return render(request, "register.html", {"form": form})

    else:
        form = RegistrationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # ----------------------------------------
        # CHECK USERNAME
        # ----------------------------------------
        try:

            user_obj = User.objects.get(username=username)

        except User.DoesNotExist:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login.html"
            )

        # ----------------------------------------
        # CHECK PASSWORD
        # ----------------------------------------
        if not user_obj.check_password(password):

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login.html"
            )

        # ----------------------------------------
        # CHECK IF ACCOUNT IS INACTIVE
        # ----------------------------------------
        if not user_obj.is_active:

            # ----------------------------------------
            # CHECK IF USER IS SUPERVISOR
            # ----------------------------------------
            if hasattr(user_obj, "profile"):

                role = user_obj.profile.role.lower()

                if role == "supervisor":

                    supervisor_request = (
                        SupervisorRequest.objects
                        .filter(user=user_obj)
                        .first()
                    )

                    # ----------------------------------------
                    # PENDING
                    # ----------------------------------------
                    if supervisor_request:

                        if supervisor_request.status == "PENDING":

                            messages.warning(
                                request,
                                "Your supervisor account is waiting for admin approval."
                            )

                        # ----------------------------------------
                        # REJECTED
                        # ----------------------------------------
                        elif supervisor_request.status == "REJECTED":

                            messages.error(
                                request,
                                "Your supervisor registration has been rejected."
                            )

                        # ----------------------------------------
                        # APPROVED BUT STILL INACTIVE
                        # ----------------------------------------
                        elif supervisor_request.status == "APPROVED":

                            messages.warning(
                                request,
                                "Your account has been approved but is currently inactive."
                            )

                        else:

                            messages.warning(
                                request,
                                "Your account is inactive."
                            )

                    else:

                        messages.warning(
                            request,
                            "No supervisor request was found."
                        )

                else:

                    messages.warning(
                        request,
                        "Your account is inactive."
                    )

            else:

                messages.warning(
                    request,
                    "Your account is inactive."
                )

            return render(
                request,
                "login.html"
            )

        # ----------------------------------------
        # AUTHENTICATE USER
        # ----------------------------------------
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # ----------------------------------------
            # ADMIN
            # ----------------------------------------
            if user.is_superuser or user.is_staff:

                return redirect("admin_dashboard")

            # ----------------------------------------
            # USER ROLE
            # ----------------------------------------
            if hasattr(user, "profile"):

                role = user.profile.role.lower()

                # ----------------------------------------
                # SUPERVISOR
                # ----------------------------------------
                if role == "supervisor":

                    return redirect(
                        "supervisor_dashboard"
                    )

                # ----------------------------------------
                # STUDENT
                # ----------------------------------------
                elif role == "student":

                    return redirect(
                        "dashboard"
                    )

            # ----------------------------------------
            # DEFAULT
            # ----------------------------------------
            return redirect("dashboard")

        # ----------------------------------------
        # AUTHENTICATION FAILED
        # ----------------------------------------
        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "login.html"
    )

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
@login_required
def milestone_tasks(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id, project__in=request.user.projects.all())
    tasks = milestone.tasks.all()
    project = milestone.project

    context = {
        'project': project,
        'milestone': milestone,
        'tasks': tasks,
        'team_members': project.members.all(),
    }
    return render(request, 'milestone_tasks.html', context)


@login_required
def add_task(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id, project__in=request.user.projects.all())

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        assigned_to_id = request.POST.get('assigned_to') or None
        priority = request.POST.get('priority', 'medium')
        start_date = request.POST.get('start_date') or None
        due_date = request.POST.get('due_date') or None

        if title and due_date:
            Task.objects.create(
                project=milestone.project,
                milestone=milestone,
                title=title,
                description=description,
                assigned_to_id=assigned_to_id,
                priority=priority,
                start_date=start_date,
                due_date=due_date,
            )
            messages.success(request, "Task added successfully!")
        else:
            messages.error(request, "Task name and due date are required.")

    return redirect('milestone_tasks', milestone_id=milestone.id)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__in=request.user.projects.all())

    context = {
        'project': task.project,
        'milestone': task.milestone,
        'task': task,
        'team_members': task.project.members.all(),
    }
    return render(request, 'task_detail.html', context)


@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__in=request.user.projects.all())

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Task.STATUS_CHOICES):
            task.status = status
            task.progress_percentage = 100 if status == 'completed' else task.progress_percentage
            task.save()
            messages.success(request, "Task status updated.")

    return redirect('task_detail', task_id=task.id)


@login_required
def upload_task_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__in=request.user.projects.all())

    if request.method == 'POST' and request.FILES.get('file'):
        TaskAttachment.objects.create(task=task, file=request.FILES['file'])
        messages.success(request, "File uploaded.")

    return redirect('task_detail', task_id=task.id)


@login_required
def milestones_view(request, project_id):
    project = get_object_or_404(request.user.projects, id=project_id)
    milestones = project.milestones.all()

    for m in milestones:
        m.task_total = m.tasks.count()
        m.task_completed = m.tasks.filter(status='completed').count()

    context = {
        'project': project,
        'milestones': milestones,
    }
    return render(request, 'milestones.html', context)


@login_required
def add_milestone(request, project_id):
    project = get_object_or_404(request.user.projects, id=project_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None

        if name:
            next_order = project.milestones.count() + 1
            Milestone.objects.create(
                project=project,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                order=next_order,
            )
            messages.success(request, "Milestone added successfully!")
        else:
            messages.error(request, "Milestone name is required.")

    return redirect('milestones', project_id=project.id)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(request.user.projects, id=project_id)

    tasks = project.tasks.all()
    milestones = project.milestones.all()

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now().date()
    ).exclude(status='completed').count()

    progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    context = {
        'project': project,
        'milestones': milestones,
        'milestone_count': milestones.count(),
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'progress_percentage': progress_percentage,
        'team_members': project.members.all(),
        'activities': project.activities.all()[:5],
    }
    return render(request, 'project_detail.html', context)


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