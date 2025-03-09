#forms.py
from django import forms
from .models import Comment
from .models import Analysis
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from django import forms

class AddClassForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})

class AnalysisForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = ['title', 'content','image']  # Başlık ve içerik için alanları seçiyoruz
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Kullanıcı yalnızca yorum metnini girebilir

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'is_premium']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'user']
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']  # Burada sadece profil resmini alıyoruz.


class PasswordUpdateForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)