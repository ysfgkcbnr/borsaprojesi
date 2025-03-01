from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from borsa.views import chat_room  # Buraya chat_room fonksiyonunu import edin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('borsa.urls')),  # Borsa uygulamasının URL'lerini dahil et
    path('chat/', chat_room, name='chat_room'),  # Chat odası URL'si
]

# Statik ve medya dosyalarını düzgün göstermek için
if settings.DEBUG:  # Sadece geliştirme modunda çalıştır
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
