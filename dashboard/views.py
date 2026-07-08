from django.shortcuts import render


def dashboard_view(request):
    # This dictionary will hold the dynamic data you fetch from your database later.
    # For now, it passes the context needed to render your template.
    context = {
        'project_name': 'Smart Library Management System',
        'team_leader': 'John Doe',
    }
    return render(request, 'dashboard.html', context)
# Create your views here.
