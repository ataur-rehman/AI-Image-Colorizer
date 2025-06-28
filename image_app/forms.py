from django import forms
from .models import Profile , Image

class signup_form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Profile
        fields = ['username' , 'email' , 'password' ,'membership_type']
        
class login_form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Profile
        fields = ['username' , 'password']
        
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['original_image']