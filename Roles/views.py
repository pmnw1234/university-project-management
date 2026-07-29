from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SupervisorRequest
from .forms import SupervisorRequestForm, SupervisorAccountCreateForm

def supervisor_request(request):
    if request.method == 'POST':
        form = SupervisorRequestForm(request.POST)
        if form.is_valid():
            req_obj = form.save()
            return redirect('supervisor_status', request_id=req_obj.id)
    else:
        form = SupervisorRequestForm()
    return render(request, 'supervisor_request.html', {'form': form})

def supervisor_status(request, request_id):
    req_obj = get_object_or_404(SupervisorRequest, id=request_id)
    return render(request, 'supervisor_status.html', {'req_obj': req_obj})

@login_required
def system_logs(request):
    pending_requests = SupervisorRequest.objects.filter(status='PENDING').order_by('-created_at')
    all_requests = SupervisorRequest.objects.all().order_by('-created_at')
    context = {
        'pending_requests': pending_requests,
        'all_requests': all_requests
    }
    return render(request, 'admin_supervisor_requests.html', context)

@login_required
def approve_supervisor_request(request, request_id):
    req_obj = get_object_or_404(SupervisorRequest, id=request_id)
    req_obj.status = 'APPROVED'
    req_obj.save()
    messages.success(request, 'Supervisor request approved successfully.')
    return redirect('system_logs')

@login_required
def reject_supervisor_request(request, request_id):
    req_obj = get_object_or_404(SupervisorRequest, id=request_id)
    req_obj.status = 'REJECTED'
    req_obj.save()
    messages.warning(request, 'Supervisor request rejected.')
    return redirect('system_logs')

def supervisor_register(request, request_id):
    req_obj = get_object_or_404(SupervisorRequest, id=request_id)
    if req_obj.status != 'APPROVED':
        return render(request, 'supervisor_status.html', {'req_obj': req_obj})

    if request.method == 'POST':
        form = SupervisorAccountCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = SupervisorAccountCreateForm(initial={
            'email': req_obj.email,
            'first_name': req_obj.first_name,
            'last_name': req_obj.last_name
        })
    return render(request, 'supervisor_signup.html', {'form': form, 'req_obj': req_obj})