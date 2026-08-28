from django.db import models
from django.contrib.auth.models import User

class SupervisorRequest(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    email = models.EmailField(unique=True)

    department = models.CharField(
        max_length=100
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )