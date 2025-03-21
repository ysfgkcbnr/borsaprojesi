#urls.py
from django.contrib.auth import views as auth_views
from . import views
from .views import chat_room
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [

    path('', views.borsa_anasayfa, name='anasayfa'),
    path('about/', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout1.html'), name='logout'),
    # auth_views.LogoutView kullanılıyor
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('register/', views.register, name='register'),
    path('analysis/', views.analysis_list, name='analysis_list'),
    path('add_analysis/', views.add_analysis, name='add_analysis'),
    path('add_comment/<int:analysis_id>/', views.add_comment, name='add_comment'),
    path('like_analysis/<int:analysis_id>/', views.like_analysis, name='like_analysis'),
    path('save_analysis/<int:analysis_id>/', views.save_analysis, name='save_analysis'),
    path('saved_analyses/', views.saved_analyses, name='saved_analyses'),
    path('edit_analysis/<int:analysis_id>/', views.edit_analysis, name='edit_analysis'),
    path('delete_analysis/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('notifications/', views.notifications, name='notifications'),
    path('premium_analysis_list/', views.premium_analysis_list, name='premium_analysis_list'),
    path('chat_room/', chat_room, name='chat_room'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('tracking_list/', views.tracking_list, name='tracking_list'),
    path('track/add/<int:hisse_id>/', views.add_to_tracking, name='add_to_tracking'),
    path('track/remove/<int:hisse_id>/', views.remove_from_tracking, name='remove_from_tracking'),
    path('alarm/set/<int:hisse_id>/', views.set_alarm, name='set_alarm'),
    path('alarm/remove/<int:alarm_id>/', views.remove_alarm, name='remove_alarm'),
 ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
