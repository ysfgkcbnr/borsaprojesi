from django.contrib import admin
from .models import Hisse
from .models import Analysis, Comment, Like, Saved



admin.site.register(Hisse)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Saved)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at', 'is_premium']  # Görüntülenecek alanları belirledik
    list_filter = ('is_premium', 'author')  # Filtreleme ekleyelim
    search_fields = ('title',)  # Başlığa göre arama yapabilme
    fields = ('title', 'content', 'image', 'is_premium', 'author')  # Admin panelinde düzenleme alanları

admin.site.register(Analysis, AnalysisAdmin)  # Doğru kayıt şekli