#views.py
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
from django.shortcuts import render
import yfinance as yf
from .models import Hisse2
from .models import UserStockTracking
from .models import StockAlarm
from django.db.models import Q
import time  # Bunu dosyanın başına ekle


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Başarıyla kayıt oldunuz! Giriş yapabilirsiniz.")
            return redirect('login')
        else:
            print(form.errors)  # Hata mesajlarını terminale yazdır
            messages.error(request, "Kayıt sırasında bir hata oluştu!")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def set_alarm(request, hisse_id):
    hisse = get_object_or_404(Hisse2, id=hisse_id)
    if request.method == 'POST':
        threshold = float(request.POST.get('threshold'))
        is_above = request.POST.get('is_above') == 'above'
        StockAlarm.objects.create(user=request.user, hisse=hisse, threshold=threshold, is_above=is_above)
        return redirect('tracking_list')
    return render(request, 'registration/set_alarm.html', {'hisse': hisse})

@login_required
def remove_alarm(request, alarm_id):
    alarm = get_object_or_404(StockAlarm, id=alarm_id, user=request.user)
    alarm.delete()
    return redirect('tracking_list')

@login_required
def tracking_list(request):
    tracked_stocks = UserStockTracking.objects.filter(user=request.user)
    return render(request, 'registration/tracking_list.html', {'tracked_stocks': tracked_stocks})

@login_required
def add_to_tracking(request, hisse_id):
    hisse = get_object_or_404(Hisse2, id=hisse_id)
    UserStockTracking.objects.get_or_create(user=request.user, hisse=hisse)
    return redirect('tracking_list')

@login_required
def remove_from_tracking(request, hisse_id):
    hisse = get_object_or_404(Hisse2, id=hisse_id)
    UserStockTracking.objects.filter(user=request.user, hisse=hisse).delete()
    return redirect('tracking_list')


def borsa_anasayfa(request):
    print("View çalışıyor aga!")
    XU30_HISSELERI = ['GARAN', 'AKBNK', 'ISCTR']
    XU100_HISSELERI = ['XU100', 'THYAO', 'GARAN', 'AKBNK', 'ISCTR']

    EXCHANGE_MAP = {
        'XIST': 'BIST',
        'NMS': 'NASDAQ',
        'NYQ': 'NYSE',
    }

    try:
        hisse_sembolleri = {
            "XU100.IS": "XU100",
            "GARAN.IS": "GARAN",
            "THYAO.IS": "THYAO",
        }

        for sembol, isim in hisse_sembolleri.items():
            ticker = yf.Ticker(sembol)
            tarih_veri = ticker.history(period="2d")
            info = ticker.info
            print(f"{isim} için çekilen veri:", tarih_veri)

            if not tarih_veri.empty and len(tarih_veri) >= 2:
                onceki_kapanis = tarih_veri['Close'].iloc[-2]
                bugunku_kapanis = tarih_veri['Close'].iloc[-1]
                degisim_yuzdesi = ((
                                               bugunku_kapanis - onceki_kapanis) / onceki_kapanis) * 100 if onceki_kapanis != 0 else 0

                is_xu30 = isim in XU30_HISSELERI
                is_xu100 = isim in XU100_HISSELERI
                exchange = EXCHANGE_MAP.get(info.get('exchange', 'BIST'), info.get('exchange', 'BIST'))
                hisse, created = Hisse2.objects.get_or_create(
                    isim=isim,
                    defaults={
                        'fiyat': round(bugunku_kapanis, 2),
                        'fiyat_degisim_yuzdesi': round(degisim_yuzdesi, 2),
                        'hacim': int(tarih_veri['Volume'].iloc[-1]),
                        'is_bisttum': True,
                        'is_xu100': is_xu100,
                        'is_xu30': is_xu30,
                        'exchange': exchange,
                    }
                )
                if not created:
                    hisse.fiyat = round(bugunku_kapanis, 2)
                    hisse.fiyat_degisim_yuzdesi = round(degisim_yuzdesi, 2)
                    hisse.hacim = int(tarih_veri['Volume'].iloc[-1])
                    hisse.is_bisttum = True
                    hisse.is_xu100 = is_xu100
                    hisse.is_xu30 = is_xu30
                    hisse.exchange = exchange
                    hisse.save()

        data = Hisse2.objects.all()
        arama = request.GET.get('arama', '').strip().upper()
        siralama = request.GET.get('siralama', 'isim')
        kategori = request.GET.get('kategori', 'TÜM HİSSELER')

        if arama:
            data = data.filter(isim__icontains=arama)
            if not data.exists():
                try:
                    ticker = yf.Ticker(arama)
                    tarih_veri = ticker.history(period="2d")
                    info = ticker.info
                    if not tarih_veri.empty and len(tarih_veri) >= 2:
                        onceki_kapanis = tarih_veri['Close'].iloc[-2]
                        bugunku_kapanis = tarih_veri['Close'].iloc[-1]
                        degisim_yuzdesi = ((
                                                       bugunku_kapanis - onceki_kapanis) / onceki_kapanis).__float__() * 100 if onceki_kapanis != 0 else 0
                        exchange = EXCHANGE_MAP.get(info.get('exchange', 'N/A'), info.get('exchange', 'N/A'))
                        hisse, created = Hisse2.objects.get_or_create(
                            isim=arama,
                            defaults={
                                'fiyat': round(bugunku_kapanis, 2),
                                'fiyat_degisim_yuzdesi': round(degisim_yuzdesi, 2),
                                'hacim': int(tarih_veri['Volume'].iloc[-1]),
                                'is_bisttum': False,
                                'is_xu100': False,
                                'is_xu30': False,
                                'exchange': exchange,
                            }
                        )
                        data = Hisse2.objects.filter(isim=arama)
                except Exception as e:
                    print(f"Yahoo arama hatası: {str(e)}")
        else:
            if kategori == 'XU30':
                data = data.filter(is_xu30=True)
            elif kategori == 'XU100':
                data = data.filter(is_xu100=True)
            elif kategori == 'BISTTÜM':
                data = data.filter(is_bisttum=True)
            elif kategori != 'TÜM HİSSELER':
                data = data.filter(exchange=kategori)

            if siralama == 'fiyat':
                data = data.order_by('fiyat')
            elif siralama == 'degisim':
                data = data.order_by('fiyat_degisim_yuzdesi')
            elif siralama == 'hacim':
                data = data.order_by('hacim')
            else:
                data = data.order_by('isim')

        borsa_kategorileri = list(Hisse2.objects.values_list('exchange', flat=True).distinct())
        kategori_secenekleri = {
            'TÜM HİSSELER': kategori == 'TÜM HİSSELER',
            'BISTTÜM': kategori == 'BISTTÜM',
            'XU30': kategori == 'XU30',
            'XU100': kategori == 'XU100',
        }
        for borsa in borsa_kategorileri:
            kategori_secenekleri[borsa] = kategori == borsa

        siralama_secenekleri = {
            'isim': siralama == 'isim',
            'fiyat': siralama == 'fiyat',
            'degisim': siralama == 'degisim',
            'hacim': siralama == 'hacim',
        }

        print("Veritabanındaki veriler:", list(data))
    except Exception as e:
        print("Hata var aga:", str(e))
        data = []
        arama = ''  # Varsayılan değer eklendi
        siralama = 'isim'
        kategori = 'TÜM HİSSELER'
        siralama_secenekleri = {
            'isim': True,
            'fiyat': False,
            'degisim': False,
            'hacim': False,
        }
        kategori_secenekleri = {
            'TÜM HİSSELER': True,
            'BISTTÜM': False,
            'XU30': False,
            'XU100': False,
        }
        borsa_kategorileri = []  # Varsayılan boş liste

    return render(request, 'index.html', {
        'data': data,
        'arama': arama,
        'siralama': siralama,
        'kategori': kategori,
        'siralama_secenekleri': siralama_secenekleri,
        'kategori_secenekleri': kategori_secenekleri,
        'borsa_kategorileri': borsa_kategorileri
    })

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

    return render(request, 'registration/update_profile.html', {
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

    return render(request, "registration/login.html")