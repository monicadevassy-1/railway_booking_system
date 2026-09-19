from django import forms
from .models import RailwayUser

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = RailwayUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "gender",
            "date_of_birth",]

class LoginForm(forms.ModelForm):
    class Meta:
        model = RailwayUser
        fields = [
            "username",
            "password",]



class AdminProfileForm(forms.ModelForm):
    new_password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=False)
    # means the admin doesn't have to enter a new password when only changing their name, email, phone, etc.
    class Meta:
        model = RailwayUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'gender',
            'date_of_birth',
            "password"]