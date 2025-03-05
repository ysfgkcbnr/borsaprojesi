#models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class StockAlarm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hisse = models.ForeignKey('Hisse2', on_delete=models.CASCADE)
    threshold = models.FloatField()  # Fiyat eşiği
    is_above = models.BooleanField(default=True)  # Üstüne mi, altına mı alarm
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hisse.isim} @ {self.threshold}"
class UserStockTracking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hisse = models.ForeignKey('Hisse2', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hisse')  # Bir kullanıcı bir hisseyi birden fazla ekleyemez

    def __str__(self):
        return f"{self.user.username} - {self.hisse.isim}"


class Hisse2(models.Model):
    isim = models.CharField(max_length=10, unique=True)
    fiyat = models.FloatField()
    fiyat_degisim_yuzdesi = models.FloatField(default=0.0)
    hacim = models.BigIntegerField()
    zaman = models.DateTimeField(auto_now=True)
    is_bisttum = models.BooleanField(default=True)  # Tüm hisseler BISTTUM’da
    is_xu100 = models.BooleanField(default=False)  # BIST 100 için
    is_xu30 = models.BooleanField(default=False)   # BIST 30 için

    def __str__(self):
        return self.isim

# Yöneticilerin paylaştığı analizler için model
class Analysis(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class Comment(models.Model):
    analysis = models.ForeignKey(Analysis, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()  # Yorum içeriği
    image = models.ImageField(upload_to='comments/', null=True, blank=True)  # Fotoğraf eklemek için
    created_at = models.DateTimeField(auto_now_add=True)  # Yorumun oluşturulma tarihi

    def __str__(self):
        return f"Comment by {self.user.username}"

# Beğeniler için model

class Like(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('analysis', 'user')  # Bir kullanıcı sadece bir analizi bir kez beğenebilir.

    def __str__(self):
        return f"{self.user.username} liked {self.analysis.title}"

class Saved(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('analysis', 'user')  # Bir kullanıcı sadece bir analizi bir kez kaydedebilir.

    def __str__(self):
        return f"{self.user.username} saved {self.analysis.title}"

class Hisse(models.Model):
    isim = models.CharField(max_length=100)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.isim


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')  # Bir kullanıcı aynı yorumu yalnızca bir kez beğenebilir.




class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


class CustomUser(AbstractUser):

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profil resmi
    is_premium = models.BooleanField(default=False)  # Premium kullanıcı mı?

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username