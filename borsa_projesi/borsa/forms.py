from django import forms
from .models import Comment
from .models import Analysis

class AnalysisForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = ['title', 'content','image']  # Başlık ve içerik için alanları seçiyoruz
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Kullanıcı yalnızca yorum metnini girebilir
