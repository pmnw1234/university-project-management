from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Team, TeamInvitation

def team_view(request):
    user = request.user
    
    # 1. Fetch all teams the user leads or has joined
    led_teams = Team.objects.filter(leader=user)
    joined_teams = Team.objects.filter(members=user).exclude(leader=user)
    all_teams = (led_teams | joined_teams).distinct()

    # 2. Determine which team is selected/active
    team_id = request.GET.get('team_id')
    active_team = None
    if team_id:
        active_team = all_teams.filter(id=team_id).first()
    
    # Fall back to the first team if no valid team_id is supplied
    if not active_team and all_teams.exists():
        active_team = all_teams.first()

    # 3. Handle search inside the active team context
    search_query = request.GET.get('search', '')
    searched_students = []
    if search_query and active_team:
        searched_students = User.objects.filter(username__icontains=search_query).exclude(id__in=active_team.members.all())

    # 4. Fetch pending invitations for the logged-in user
    pending_invitations = TeamInvitation.objects.filter(invited_user=user, status='pending')

    context = {
        'all_teams': all_teams,
        'active_team': active_team,
        'search_query': search_query,
        'searched_students': searched_students,
        'pending_invitations': pending_invitations,
    }
    return render(request, 'teams.html', context)

@login_required
def create_team(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if team_name:
            if Team.objects.filter(leader=request.user).exists():
                messages.error(request, "You are already a team leader of a team!")
            else:
                team = Team.objects.create(name=team_name, leader=request.user)
                team.members.add(request.user)
                messages.success(request, f"Team '{team_name}' created successfully!")
    return redirect('team_view')

@login_required
def send_invitation(request, student_id):
    team = get_object_or_404(Team, leader=request.user)
    student = get_object_or_404(User, id=student_id)
    
    invitation, created = TeamInvitation.objects.get_or_create(
        team=team, invited_user=student, status='pending'
    )
    if created:
        messages.success(request, f"Invitation sent to {student.username}!")
    else:
        messages.warning(request, f"Invitation already sent to {student.username}.")
        
    return redirect('team_view')

@login_required
def respond_invitation(request, invitation_id, action):
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, invited_user=request.user)
    
    if action == 'accept':
        invitation.status = 'accepted'
        invitation.save()
        invitation.team.members.add(request.user)
        messages.success(request, f"You joined team '{invitation.team.name}'!")
    elif action == 'decline':
        invitation.status = 'declined'
        invitation.save()
        messages.info(request, f"Declined invitation to '{invitation.team.name}'.")
        
    return redirect('team_view')

@login_required
def remove_member(request, member_id):
    team = get_object_or_404(Team, leader=request.user)
    member_to_remove = get_object_or_404(User, id=member_id)
    
    if member_to_remove != request.user:
        team.members.remove(member_to_remove)
        messages.success(request, f"Removed {member_to_remove.username} from the team.")
    else:
        messages.error(request, "You cannot remove yourself as leader.")
        
    return redirect('team_view')