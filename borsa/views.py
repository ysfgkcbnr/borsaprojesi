from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from yahoo_fin import stock_info
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import Analysis, Comment, Like, Saved
from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from .forms import AnalysisForm
from django.contrib import messages
from .models import Comment, CommentLike
from .models import Notification
from .models import Analysis
from .decorators import premium_required
from .models import Comment
from django.shortcuts import render
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from .forms import ProfileForm
from .models import UserProfile
from .forms import UserProfileForm
from .forms import ProfileUpdateForm, PasswordUpdateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import yfinance as yf
from django.shortcuts import render


def index(request):
    # Hisse senedi sembollerini belirleyin
    tickers = ['THYAO.IS', 'GARAN.IS', 'SAHOL.IS']

    # Verileri çekmek için bir sözlük oluşturuyoruz
    data = {}

    for ticker in tickers:
        # Yfinance ile hisse verisini çekiyoruz
        df = yf.download(ticker, period='1d', interval='1m')
        print(df.head())  # DataFrame'in ilk 5 satırını yazdır

        # Fiyat değişim oranını ekliyoruz
        df['Price Change (%)'] = df['Close'].pct_change() * 100

        # NaN değerleri temizliyoruz
        df = df.dropna(subset=['Price Change (%)'])

        # Son satırdaki veriyi alıyoruz (en son kapanış fiyatı ve diğer veriler)
        latest_data = df.iloc[-1]

        # Veriyi dictionary'ye ekliyoruz
        data[ticker] = {
            'close': latest_data['Close'],
            'price_change': latest_data['Price Change (%)'],
            'volume': latest_data['Volume'],
        }

    # Verileri render ederken 'data' isimli dictionary'yi şablona gönderiyoruz
    return render(request, 'index.html', {'data': data})


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()  # Profil resmi güncelle
            password_form.save()  # Şifreyi güncelle
            update_session_auth_hash(request, request.user)  # Oturumu güncelle
            return redirect('profile')  # Profil sayfasına yönlendir

    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'update_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })
@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            return redirect('profile')  # Kullanıcı profil sayfasına yönlendiriliyor

    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'registration/update_profile.html', {'form': form, 'user_profile': user_profile})
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Kayıt olduktan sonra login sayfasına yönlendir
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Kullanıcı kaydı fonksiyonunu tek bir şekilde tanımlayın:

@login_required
def profile_view(request):
    user_profile = request.user.profile  # Kullanıcıya ait profil bilgileri

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Güncelleme işlemi başarılı olursa profil sayfasına yönlendir
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'registration/profile.html', {'form': form, 'user_profile': user_profile})

def chat_room(request):
    return render(request, 'registration/chat.html')

@premium_required  # Yalnızca premium kullanıcılar görebilir
def premium_analysis_list(request):
    analyses = Analysis.objects.filter(is_premium=True)  # Premium analizleri getir
    return render(request, 'registration/premium_analysis_list.html', {'analyses': analyses})

def premium_info(request):
    return render(request, 'registration/premium_info.html')

def analysis_list(request):
    search_query = request.GET.get('q', '')  # Arama sorgusu
    if search_query:
        analyses = Analysis.objects.filter(title__icontains=search_query)  # Başlıkta arama
    else:
        analyses = Analysis.objects.all()
    return render(request, 'registration/analysis_list.html', {'analyses': analyses, 'search_query': search_query})

# Analize yorum eklemek
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
            return redirect('analysis_list')  # Yorum eklendikten sonra geri dön
    else:
        form = CommentForm()
    return render(request, 'registration/add_comment.html', {'form': form, 'analysis': analysis})

# Analizi beğenmek
@login_required
def like_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)
    Like.objects.create(analysis=analysis, user=request.user)
    messages.success(request, 'Analiz başarıyla beğenildi!')
    return redirect('analysis_list')

# Analizi kaydetmek
@login_required
def save_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)
    Saved.objects.create(analysis=analysis, user=request.user)
    messages.success(request, 'Analiz başarıyla kaydedildi!')
    return redirect('analysis_list')

# Analiz eklemek
@login_required
def add_analysis(request):
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.author = request.user  # Yöneticinin kim olduğunu kaydediyoruz
            analysis.save()
            return redirect('analysis_list')  # Analiz eklendikten sonra analizler sayfasına dönüyoruz
    else:
        form = AnalysisForm()
    return render(request, 'registration/add_analysis.html', {'form': form})

# Kullanıcının kaydettiği analizler
@login_required
def saved_analyses(request):
    saved_analyses = Saved.objects.filter(user=request.user)
    return render(request, 'registration/saved_analyses.html', {'saved_analyses': saved_analyses})
@login_required
def analysis_list(request):
    if request.user.is_superuser:
        analyses = Analysis.objects.all()  # Yöneticiler için tüm analizler
    else:
        analyses = Analysis.objects.filter(author=request.user)  # Normal kullanıcılar için yalnızca kendi analizleri
    return render(request, 'registration/analysis_list.html', {'analyses': analyses})


# Analiz düzenleme
@login_required
def edit_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)

    if analysis.author != request.user and not request.user.is_superuser:
        return redirect('analysis_list')  # Kullanıcı yalnızca kendi analizlerini düzenleyebilir

    if request.method == 'POST':
        form = AnalysisForm(request.POST, instance=analysis)
        if form.is_valid():
            form.save()
            return redirect('analysis_list')
    else:
        form = AnalysisForm(instance=analysis)

    return render(request, 'borsa/edit_analysis.html', {'form': form, 'analysis': analysis})

# Analiz silme
@login_required
def delete_analysis(request, analysis_id):
    analysis = get_object_or_404(Analysis, id=analysis_id)

    if analysis.author != request.user and not request.user.is_superuser:
        return redirect('analysis_list')  # Kullanıcı yalnızca kendi analizlerini silebilir

    analysis.delete()
    return redirect('analysis_list')

# views.py
@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if not CommentLike.objects.filter(comment=comment, user=request.user).exists():
        CommentLike.objects.create(comment=comment, user=request.user)
    return redirect('analysis_list')  # Yorumlar sayfasına geri dön

# views.py
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user and not request.user.is_superuser:
        return redirect('analysis_list')  # Kullanıcı yalnızca kendi yorumlarını silebilir
    comment.delete()
    return redirect('analysis_list')


def custom_logout(request):
    logout(request)
    return redirect('login')
def index(request):
    return render(request, 'index.html')

def about(request):
    return HttpResponse("Bu, borsa ile ilgili bir projedir.")



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
                user=analysis.author,  # Yorum yapan kişi yöneticiyi bildirecek
                message=f'{request.user.username} yorum yaptı: {comment.text}'
            )

            return redirect('analysis_list')
    else:
        form = CommentForm()
    return render(request, 'registration/add_comment.html', {'form': form, 'analysis': analysis})

# views.py
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'registration/notifications.html', {'notifications': notifications})

@login_required
def premium_page(request):
    if request.user.is_premium:
        return render(request, 'registration/premium.html')
    else:
        return render(request, 'registration/not_premium.html')


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/profile/")  # Başarıyla giriş yapınca yönlendir
        else:
            return render(request, "login.html", {"error": "Geçersiz kullanıcı adı veya şifre"})

    return render(request, "login.html")