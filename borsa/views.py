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

    # XU30 ve XU100 listeleri (senin eklemen gerekenler için şimdilik böyle)
    XU30_HISSELERI = [
        'AEFES', 'AKBNK', 'ALARK', 'ASELS', 'ASTOR', 'BIMAS', 'EKGYO', 'ENKAI', 'EREGL', 'FROTO',
        'GARAN', 'HEKTS', 'ISCTR', 'KCHOL', 'KONTR', 'KOZAL', 'KRDMD', 'MGROS', 'PETKM', 'PGSUS',
        'SAHOL', 'SASA', 'SISE', 'TCELL', 'THYAO', 'TOASO', 'TTKOM', 'TUPRS', 'ULKER', 'YKBNK'
    ]
    XU100_HISSELERI = [
        'AEFES', 'AGHOL', 'AGROT', 'AKBNK', 'AKFYE', 'AKSA', 'AKSEN', 'ALARK', 'ALFAS', 'ALTNY',
        'ANHYT', 'ANSGR', 'ARCLK', 'ARDYZ', 'ASELS', 'ASTOR', 'BERA', 'BIMAS', 'BRSAN', 'BRYAT',
        'BSOKE', 'BTCIM', 'CANTE', 'CCOLA', 'CIMSA', 'CLEBI', 'CVKMD', 'CWENE', 'DOAS', 'DOHOL',
        'ECILC', 'EGEEN', 'EKGYO', 'ENERY', 'ENJSA', 'ENKAI', 'EREGL', 'EUPWR', 'FENER', 'FROTO',
        'GARAN', 'GESAN', 'GOLTS', 'GUBRF', 'HALKB', 'HEKTS', 'IEYHO', 'ISCTR', 'ISMEN', 'KARSN',
        'KCAER', 'KCHOL', 'KLSER', 'KONTR', 'KONYA', 'KOZAA', 'KOZAL', 'KRDMD', 'LIDER', 'MAGEN',
        'MAVI', 'MGROS', 'MIATK', 'MPARK', 'NTHOL', 'ODAS', 'OTKAR', 'OYAKC', 'PASEU', 'PETKM',
        'PGSUS', 'REEDR', 'SAHOL', 'SASA', 'SDTTR', 'SELEC', 'SISE', 'SKBNK', 'SMRTG', 'SOKM',
        'TABGD', 'TAVHL', 'TCELL', 'THYAO', 'TKFEN', 'TMSN', 'TOASO', 'TSKB', 'TSPOR', 'TTKOM',
        'TTRAK', 'TUKAS', 'TUPRS', 'TURSG', 'ULKER', 'VAKBN', 'VESTL', 'YEOTK', 'YKBNK', 'ZOREN'
    ]

    EXCHANGE_MAP = {
        'XIST': 'BIST',
        'NMS': 'NASDAQ',
        'NYQ': 'NYSE',
    }

    # Listenden gelen tüm hisse sembolleri (dinamik olarak eklenecek)
    tum_hisseler = [
        "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT",
        "AGYO", "AHGAZ", "AHSGY", "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFIS", "AKFYE", "AKGRT",
        "AKMGY", "AKSA", "AKSEN", "AKSGY", "AKSUE", "AKYHO", "ALARK", "ALBRK", "ALCAR", "ALCTL",
        "ALFAS", "ALGYO", "ALKA", "ALKIM", "ALKLC", "ALMAD", "ALTNY", "ALVES", "ANELE", "ANGEN",
        "ANHYT", "ANSGR", "APBDL", "APLIB", "APX30", "ARASE", "ARCLK", "ARDYZ", "ARENA", "ARMGD",
        "ARSAN", "ARTMS", "ARZUM", "ASELS", "ASGYO", "ASTOR", "ASUZU", "ATAGY", "ATAKP", "ATATP",
        "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVPGY", "AVTUR", "AYCES", "AYDEM",
        "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAHKM", "BAKAB", "BALAT", "BALSU", "BANVT",
        "BARMA", "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENY", "BIGCH",
        "BIGEN", "BIMAS", "BINBN", "BINHO", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL",
        "BNTAS", "BOBET", "BORLS", "BORSK", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRKVY", "BRLSM",
        "BRMEN", "BRSAN", "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BULGS", "BURCE", "BURVA", "BVSAN",
        "BYDNR", "CANTE", "CASA", "CATES", "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEMZY", "CEOEM",
        "CGCAM", "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO", "CRDFA", "CRFSA", "CUSAN",
        "CVKMD", "CWENE", "DAGHL", "DAGI", "DAPGM", "DARDL", "DCTTR", "DENGE", "DERHL", "DERIM",
        "DESA", "DESPC", "DEVA", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMRGD", "DMSAS",
        "DNISI", "DOAS", "DOBUR", "DOCO", "DOFER", "DOGUB", "DOHOL", "DOKTA", "DSTKF", "DURDO",
        "DURKN", "DYOBY", "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP", "EFORC", "EGEEN",
        "EGEGY", "EGEPO", "EGGUB", "EGPRO", "EGSER", "EKGYO", "EKIZ", "EKOS", "EKSUN", "ELITE",
        "EMKEL", "EMNIS", "ENDAE", "ENERY", "ENJSA", "ENKAI", "ENSRI", "ENTRA", "EPLAS", "ERBOS",
        "ERCB", "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "ETYAT", "EUHOL", "EUKYO",
        "EUPWR", "EUREN", "EUYO", "EYGYO", "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT",
        "FORTE", "FRIGO", "FROTO", "FZLGY", "GARAN", "GARFA", "GEDIK", "GEDZA", "GENIL", "GENTS",
        "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLDTR", "GLRMK", "GLRYH", "GLYHO", "GMSTR",
        "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GRTHO", "GSDDE", "GSDHO",
        "GSRAY", "GUBRF", "GUNDG", "GWIND", "GZNMI", "HALKB", "HALKS", "HATEK", "HATSN", "HDFGS",
        "HEDEF", "HEKTS", "HKTM", "HLGYO", "HOROZ", "HRKET", "HTTBT", "HUBVC", "HUNER", "HURGZ",
        "ICBCT", "ICUGS", "IDGYO", "IEYHO", "IHAAS", "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY",
        "IMASM", "INDES", "INFO", "INGRM", "INTEK", "INTEM", "INVEO", "INVES", "IPEKE", "ISATR",
        "ISBIR", "ISBTR", "ISCTR", "ISDMR", "ISFIN", "ISGLK", "ISGSY", "ISGYO", "ISIST", "ISKPL",
        "ISKUR", "ISMEN", "ISSEN", "ISYAT", "IZENR", "IZFAS", "IZINV", "IZMDC", "JANTS", "KAPLM",
        "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KBORU", "KCAER", "KCHOL", "KENT",
        "KERVN", "KERVT", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLKIM", "KLMSN", "KLNMA", "KLRHO",
        "KLSER", "KLSYN", "KLYPV", "KMPUR", "KNFRT", "KOCMT", "KONKA", "KONTR", "KONYA", "KOPOL",
        "KORDS", "KOTON", "KOZAA", "KOZAL", "KRDMA", "KRDMB", "KRDMD", "KRGYO", "KRONT", "KRPLS",
        "KRSTL", "KRTEK", "KRVGD", "KSTUR", "KTLEV", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY",
        "KZGYO", "LIDER", "LIDFA", "LILAK", "LINK", "LKMNH", "LMKDC", "LOGO", "LRSHO", "LUKSK",
        "LYDHO", "LYDYE", "MAALT", "MACKO", "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARBL", "MARKA",
        "MARTI", "MAVI", "MEDTR", "MEGAP", "MEGMT", "MEKAG", "MEPET", "MERCN", "MERIT", "MERKO",
        "METRO", "METUR", "MGROS", "MHRGY", "MIATK", "MMCAS", "MNDRS", "MNDTR", "MOBTL", "MOGAN",
        "MOPAS", "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS",
        "NIBAS", "NTGAZ", "NTHOL", "NUGYO", "NUHCM", "OBAMS", "OBASE", "ODAS", "ODINE", "OFSYM",
        "ONCSM", "ONRYT", "OPT25", "OPTGY", "OPX30", "ORCAY", "ORGE", "ORMA", "OSMEN", "OSTIM",
        "OTKAR", "OTTO", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZATD", "OZGYO", "OZKGY", "OZRDN",
        "OZSUB", "OZYSR", "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PATEK", "PCILT", "PEHOL",
        "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR",
        "PNLSN", "PNSUT", "POLHO", "POLTK", "PRDGS", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO",
        "QNBFK", "QNBTR", "QTEMZ", "QUAGR", "RALYH", "RAYSG", "REEDR", "RGYAS", "RNPOL", "RODRG",
        "ROYAL", "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFM",
        "SANKO", "SARKY", "SASA", "SAYAS", "SDTTR", "SEGMN", "SEGYO", "SEKFK", "SEKUR", "SELEC",
        "SELGD", "SELVA", "SERNT", "SEYKM", "SILVR", "SISE", "SKBNK", "SKTAS", "SKYLP", "SKYMD",
        "SMART", "SMRTG", "SMRVA", "SNGYO", "SNICA", "SNKRN", "SNPAM", "SODSN", "SOKE", "SOKM",
        "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY", "SUWEN", "TABGD", "TARKM", "TATEN", "TATGD",
        "TAVHL", "TBORG", "TCELL", "TCKRC", "TDGYO", "TEKTU", "TERA", "TEZOL", "TGSAS", "THYAO",
        "TKFEN", "TKNSA", "TLMAN", "TMPOL", "TMSN", "TNZTP", "TOASO", "TRCAS", "TRGYO", "TRILC",
        "TSGYO", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURGG",
        "TURSG", "UFUK", "ULAS", "ULKER", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNLU", "USAK",
        "USDTR", "VAKBN", "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERTU", "VERUS", "VESBE", "VESTL",
        "VKFYO", "VKGYO", "VKING", "VRGYO", "VSNMD", "X030S", "X100S", "XBANA", "XBANK", "XBLSM",
        "XELKT", "XFINK", "XGIDA", "XGMYO", "XHARZ", "XHOLD", "XILTM", "XINSA", "XKAGT", "XKMYA",
        "XKOBI", "XKURY", "XMADN", "XMANA", "XMESY", "XSADA", "XSANK", "XSANT", "XSBAL", "XSBUR",
        "XSDNZ", "XSGRT", "XSIST", "XSIZM", "XSKAY", "XSKOC", "XSKON", "XSPOR", "XSTKR", "XTAST",
        "XTCRT", "XTEKS", "XTM25", "XTMTU", "XTRZM", "XTUMY", "XU030", "XU050", "XU100", "XUHIZ",
        "XULAS", "XUMAL", "XUSIN", "XUSRD", "XUTEK", "XUTUM", "XYLDZ", "XYORT", "XYUZO", "YAPRK",
        "YATAS", "YAYLA", "YBTAS", "YEOTK", "YESIL", "YGGYO", "YGYO", "YIGIT", "YKBNK", "YKSLN",
        "YONGA", "YUNSA", "YYAPI", "YYLGD", "Z30EA", "Z30KE", "Z30KP", "ZEDUR", "ZELOT", "ZGOLD",
        "ZOREN", "ZPBDL", "ZPLIB", "ZPT10", "ZPX30", "ZRE20", "ZRGYO", "ZSR25", "ZTM25"
    ]

    # Dinamik olarak hisse_sembolleri sözlüğünü oluştur
    hisse_sembolleri = {f"{hisse}.IS": hisse for hisse in tum_hisseler}

    try:
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
                        'is_bisttum': True,  # Hepsi BIST olduğu için True
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

        # Geri kalan kod aynı kalıyor...
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
        arama = ''
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
        borsa_kategorileri = []

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