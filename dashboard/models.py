from django.db import models
from django.contrib.auth.models import User
from team.models import Team
class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    staff_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    
    # ADD THIS LINE:
    image = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

from django.db import models
from django.contrib.auth.models import User

# --- Keep your Profile Model here ---

class Project(models.Model):
    STATUS = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Connect Project to Team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    members = models.ManyToManyField(User, related_name='projects')

    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_projects'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='draft'
    )

    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Milestone(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=255)
    progress_percentage = models.IntegerField(default=0) # 0 to 100
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField()

    def __str__(self):
        return self.title

class ActivityLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
# Create your models here.
