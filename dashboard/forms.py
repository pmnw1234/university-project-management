from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)
    student_id = forms.CharField(required=False, max_length=20)
    staff_id = forms.CharField(required=False, max_length=20) # <-- Added field

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        student_id = cleaned_data.get("student_id")
        staff_id = cleaned_data.get("staff_id")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        # Enforce rule variations conditionally
        if role == 'student' and not student_id:
            self.add_error('student_id', "Student ID is required for student accounts.")
        elif role == 'supervisor' and not staff_id:
            self.add_error('staff_id', "Staff ID is required for supervisor accounts.")
            
        return cleaned_data