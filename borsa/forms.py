from django import forms
from .models import Comment
from .models import Analysis
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

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