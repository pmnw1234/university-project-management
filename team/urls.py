from django.urls import path
from . import views

urlpatterns = [
    # ... your existing paths ...
    path('team/', views.team_view, name='team_view'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/invite/<int:student_id>/', views.send_invitation, name='send_invitation'),
    path('team/respond/<int:invitation_id>/<str:action>/', views.respond_invitation, name='respond_invitation'),
    path('team/remove/<int:member_id>/', views.remove_member, name='remove_member'),
]