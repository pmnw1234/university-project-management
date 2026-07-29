from django import forms
from django.contrib.auth.models import User
from .models import SupervisorRequest

class SupervisorRequestForm(forms.ModelForm):
    class Meta:
        model = SupervisorRequest
        fields = ['first_name', 'last_name', 'email', 'department']

class SupervisorAccountCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']