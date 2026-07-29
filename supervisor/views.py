from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import Project

@login_required
def supervisor_dashboard_view(request):
    user = request.user

    if hasattr(Project, 'supervisor'):
        supervisor_projects = Project.objects.filter(supervisor=user)
    elif hasattr(Project, 'members'):
        supervisor_projects = Project.objects.filter(members=user)
    else:
        supervisor_projects = Project.objects.none()

    total_projects = supervisor_projects.count()

    if hasattr(Project, 'status'):
        in_progress_projects = supervisor_projects.filter(status__iexact='In Progress').count()
        pending_reviews = supervisor_projects.filter(status__iexact='Pending Review').count()
        completed_projects = supervisor_projects.filter(status__iexact='Completed').count()
        at_risk_projects = supervisor_projects.filter(status__iexact='At Risk').count()
    else:
        in_progress_projects = 0
        pending_reviews = 0
        completed_projects = 0
        at_risk_projects = 0

    context = {
        'supervisor_name': user.get_full_name() or user.username,
        'projects': supervisor_projects,
        'total_projects': total_projects,
        'in_progress_projects': in_progress_projects,
        'pending_reviews': pending_reviews,
        'completed_projects': completed_projects,
        'at_risk_projects': at_risk_projects,
    }
    return render(request, 'supervisordashboard.html', context)