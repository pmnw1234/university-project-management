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
from django import forms
from django.contrib.auth.models import User
from .models import Profile  # Assuming you have a Profile model linked via OneToOneField to User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'student_id', 'staff_id']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 transition cursor-pointer'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition',
                'placeholder': 'e.g. B1234567'
            }),
            'staff_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-600 transition',
                'placeholder': 'e.g. STF98765'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        
        if self.instance and hasattr(self.instance, 'role'):
            if self.instance.role == 'student':
                self.fields.pop('staff_id', None)
                self.fields['student_id'].required = False
            elif self.instance.role == 'supervisor':
                self.fields.pop('student_id', None)
                self.fields['staff_id'].required = False
