from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, time as dtime

from .models import Event

# Төмендегілер модельдеріңде болса — импорттаймыз.
# Егер әлі жоқ болса, кейін қосасың; код try/except-пен құламайды.
try:
    from .models import Registration
except Exception:
    Registration = None

try:
    from .models import Notification
except Exception:
    Notification = None


# 🏠 Басты бет (home)
def home(request):
    return render(request, 'events/home.html')


# 🧾 Тіркелу (Register) — email міндетті, бірден логинге кіргізіп, Dashboard-қа жібереді
def register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email    = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        confirm  = request.POST.get('confirm_password') or ''

        # бос өрістер
        if not username or not email or not password:
            messages.error(request, 'Все поля должны быть заполнены!')
            return render(request, 'events/register.html')

        # құпиясөз сәйкестігі
        if password != confirm:
            messages.error(request, 'Пароли не совпадают!')
            return render(request, 'events/register.html')

        # бірегейлік тексерісі
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует!')
            return render(request, 'events/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Почта уже используется!')
            return render(request, 'events/register.html')

        # ✅ Пайдаланушыны жасау
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # ✅ Авто-логин және Dashboard-қа
        login(request, user)
        messages.success(request, 'Аккаунт успешно создан!')
        return redirect('dashboard')

    return render(request, 'events/register.html')


# 🔐 Кіру (Login) — сәтті болса Dashboard
def login_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        print(f"[LOGIN] try username='{username}'")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session.modified = True
            print(f"[LOGIN] success id={user.id}, session_key={request.session.session_key}")
            return redirect('dashboard')
        else:
            print("[LOGIN] failed")
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'events/login.html')


# 🚪 Шығу (Logout)
def logout_view(request):
    logout(request)
    return redirect('login')


# 📅 Dashboard (үлкен/шағын календарь бар бет — шаблонда визуал)
@login_required(login_url='/login/')
def dashboard(request):
    # Қажет болса, мұнда шаблонға қандай да контекст бере аламыз
    return render(request, 'events/dashboard.html')


# 🧩 FullCalendar-ға арналған JSON (барлық іс-шаралар)
@login_required(login_url='/login/')
def events_json(request):
    events = Event.objects.all().order_by('date')
    payload = []

    for e in events:
        # Күн+уақыт ISO-ға біріктіреміз
        t = e.time if getattr(e, 'time', None) else dtime(18, 0)
        start_iso = datetime.combine(e.date, t).isoformat()

        payload.append({
            "id": e.id,
            "title": e.title,
            "start": start_iso,               # FullCalendar үшін
            "extendedProps": {
                "place": getattr(e, 'place', ''),
                "description": getattr(e, 'description', ''),
                "capacity": getattr(e, 'capacity', None),
            }
        })

    return JsonResponse(payload, safe=False)


# 📝 Іс-шараға жазылу (capacity және дубль тексерісімен)
@login_required(login_url='/login/')
def event_signup(request, event_id):
    evt = get_object_or_404(Event, id=event_id)

    # Егер Registration моделі жоқ болса — жай ғана хабарлап қоямыз
    if Registration is None:
        messages.error(request, 'Регистрация временно недоступна (модель не подключена).')
        return redirect('dashboard')

    # Қайта жазылуды блоктау
    if Registration.objects.filter(event=evt, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы на это мероприятие.')
        return redirect('dashboard')

    # Capacity тексерісі (егер capacity атрибуты бар болса)
    cap = getattr(evt, 'capacity', None)
    if cap is not None:
        taken = Registration.objects.filter(event=evt).count()
        if taken >= cap:
            messages.error(request, 'Мест больше нет 😢')
            return redirect('dashboard')

    # Жазып қою
    Registration.objects.create(event=evt, user=request.user)

    # Хабарлама жазу (егер Notification моделі бар болса)
    try:
        if Notification is not None:
            Notification.objects.create(
                user=request.user,
                text=f"Вы записались: «{evt.title}»",
                is_read=False
            )
    except Exception as ex:
        print(f"[NOTIF] cannot create: {ex}")

    messages.success(request, 'Вы успешно зарегистрировались!')
    return redirect('my_events')


# 🧾 Менің іс-шараларым (пайдаланушының тіркелгендері)
@login_required(login_url='/login/')
def my_events(request):
    if Registration is None:
        # Егер Registration моделі жоқ болса — бос тізім
        my_regs = []
    else:
        my_regs = (Registration.objects
                   .filter(user=request.user)
                   .select_related('event')
                   .order_by('event__date'))

    return render(request, 'events/my_events.html', {
        'registrations': my_regs
    })


# 🔔 Хабарламалар тізімі (in-app notifications)
@login_required(login_url='/login/')
def notifications_list(request):
    if Notification is None:
        items = []
    else:
        items = Notification.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'events/notifications.html', {
        'notifications': items
    })


# ✅ Хабарламаны оқылды деп белгілеу
@login_required(login_url='/login/')
def notification_read(request, notif_id):
    if Notification is not None:
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    return redirect('notifications')


# 🛠️ Тек админ — Мероприятие жасау беті
@login_required(login_url='/login/')
def create_event(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        description = request.POST.get('description') or ''
        place = request.POST.get('location') or ''
        date_str = request.POST.get('date') or ''
        time_str = request.POST.get('time') or '18:00'
        cap_str  = request.POST.get('capacity') or ''

        # Күні/уақытты parse
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            messages.error(request, 'Неверная дата. Формат: ГГГГ-ММ-ДД')
            return render(request, 'events/create_event.html')

        try:
            hh, mm = [int(x) for x in time_str.split(':')]
            t = dtime(hh, mm)
        except Exception:
            t = dtime(18, 0)

        # capacity опционал
        cap_val = None
        try:
            if cap_str:
                cap_val = int(cap_str)
        except Exception:
            cap_val = None

        Event.objects.create(
            title=title,
            description=description,
            place=place,
            date=d,
            time=t,
            capacity=cap_val,
            created_by=request.user
        )
        messages.success(request, 'Мероприятие успешно создано!')
        return redirect('dashboard')

    return render(request, 'events/create_event.html')