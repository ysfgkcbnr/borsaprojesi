from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import chat_room


urlpatterns = [
    path('', views.index, name='index'),
    path('hakkında/', views.about, name='about'),
    path('giriş/', auth_views.LoginView.as_view(), name='login'),
    path('çıkış/', auth_views.LogoutView.as_view(template_name='registration/logout1.html'), name='logout'),
    # auth_views.LogoutView kullanılıyor
    path('şifre_sıfırlama/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('kayıt/', views.register, name='register'),
    path('analizler/', views.analysis_list, name='analysis_list'),
    path('analiz_ekle/', views.add_analysis, name='add_analysis'),
    path('yorum_ekle/<int:analysis_id>/', views.add_comment, name='add_comment'),
    path('analiz_begenme/<int:analysis_id>/', views.like_analysis, name='like_analysis'),
    path('analiz_kaydetme/<int:analysis_id>/', views.save_analysis, name='save_analysis'),
    path('kaydedilenler/', views.saved_analyses, name='saved_analyses'),
    path('analiz_düzenle/<int:analysis_id>/', views.edit_analysis, name='edit_analysis'),
    path('analiz_silme/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    path('yorum_begenme/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('yorum_silme/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('bildirimler/', views.notifications, name='notifications'),
    path('premium_analizler/', views.premium_analysis_list, name='premium_analysis_list'),
    path('chat/', chat_room, name='chat_room'),

]
