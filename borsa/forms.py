from django import forms
from .models import Comment
from .models import Analysis
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

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
    class Meta:
        model = User
        fields = ['password']