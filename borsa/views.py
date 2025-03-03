from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, get_object_or_404, redirect
from .models import Analysis, Comment, Like, Saved, Notification
from .forms import CommentForm, AnalysisForm, CustomUserCreationForm, ProfileUpdateForm, PasswordUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import premium_required
from .models import UserProfile

# Profil Güncelleme
@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        password_form = PasswordUpdateForm(request.user, request.POST)

        if form.is_valid() and password_form.is_valid():
            form.save()
            password_form.save()
            messages.success(request, 'Profil ve şifreniz başarıyla güncellendi.')
            return redirect('profile')

    else:
        form = ProfileUpdateForm(instance=user_profile)
        password_form = PasswordUpdateForm(request.user)

    return render(request, 'registration/update_profile.html', {
        'form': form,
        'user_profile': user_profile,
        'password_form': password_form
    })

# Kayıt
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Profil Görüntüleme ve Güncelleme
@login_required
def profile_view(request):
    user_profile = request.user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'registration/profile.html', {'form': form, 'user_profile': user_profile})

# Analiz Ekleme
@login_required
def add_analysis(request):
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.author = request.user
            analysis.save()
            return redirect('analysis_list')
    else:
        form = AnalysisForm()
    return render(request, 'registration/add_analysis.html', {'form': form})

# Analiz Listesi
@login_required
def analysis_list(request):
    analyses = Analysis.objects.all()
    return render(request, 'registration/analysis_list.html', {'analyses': analyses})

# Analiz Beğenme
@login_required
def like_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)
    Like.objects.create(analysis=analysis, user=request.user)
    messages.success(request, 'Analiz başarıyla beğenildi!')
    return redirect('analysis_list')

# Analiz Kaydetme
@login_required
def save_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)
    Saved.objects.create(analysis=analysis, user=request.user)
    messages.success(request, 'Analiz başarıyla kaydedildi!')
    return redirect('analysis_list')

# Yorum Ekleme
@login_required
def add_comment(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.analysis = analysis
            comment.user = request.user
            comment.save()

            # Bildirim oluşturma
            notification = Notification.objects.create(
                user=analysis.author,
                message=f'{request.user.username} yorum yaptı: {comment.text}'
            )

            return redirect('analysis_list')
    else:
        form = CommentForm()
    return render(request, 'registration/add_comment.html', {'form': form, 'analysis': analysis})

# Bildirimler
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'registration/notifications.html', {'notifications': notifications})

# Premium Sayfası
def premium_page(request):
    if request.user.is_premium:
        return render(request, 'registration/premium.html')
    else:
        return render(request, 'registration/not_premium.html')

# Çıkış Yapma
def custom_logout(request):
    logout(request)
    return redirect('login')

# Giriş Yapma
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/profile/")
        else:
            return render(request, "login.html", {"error": "Geçersiz kullanıcı adı veya şifre"})

    return render(request, "login.html")
