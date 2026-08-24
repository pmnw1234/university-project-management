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
        
class SupervisorRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-lg border px-3 py-2"
        })
    )

    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-lg border px-3 py-2"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full rounded-lg border px-3 py-2"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full rounded-lg border px-3 py-2"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "w-full rounded-lg border px-3 py-2"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full rounded-lg border px-3 py-2"
            }),
        }