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


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'student_id', 'staff_id']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'student_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
            'staff_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
        }

class SupervisorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'staff_id', 'department', 'phone', 'office_location', 'bio']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'file-input-custom'}),
            'staff_id': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'department': forms.Select(attrs={'class': 'form-select-custom'}, choices=[
                ('', 'Select Department'),
                ('Computer Science', 'Computer Science'),
                ('Information Technology', 'Information Technology'),
                ('Software Engineering', 'Software Engineering'),
                ('Electrical Engineering', 'Electrical Engineering'),
                ('Mechanical Engineering', 'Mechanical Engineering'),
                ('Business Administration', 'Business Administration'),
                ('Mathematics', 'Mathematics'),
                ('Physics', 'Physics'),
                ('Chemistry', 'Chemistry'),
                ('Biology', 'Biology'),
                ('Other', 'Other'),
            ]),
            'phone': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'office_location': forms.TextInput(attrs={'class': 'form-control-custom'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea-custom', 'rows': 4, 'placeholder': 'Tell us about your expertise and background...'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('image'):
            instance.image = self.cleaned_data.get('image')
        if commit:
            instance.save()
        return instance
