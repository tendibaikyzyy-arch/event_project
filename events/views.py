# events/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import Event, Registration, Notification

# -----------------------
# Көмекші функциялар
# -----------------------
def _notify(user, title, body=""):
    """Жай сайт ішіндегі (in-app) хабарлама құру."""
    try:
        Notification.objects.create(user=user, title=title, body=body)
    except Exception:
        # Хабарлама құру міндетті емес – қате болса да сайт құламасын
        pass


# -----------------------
# Басты бет
# -----------------------
def home(request):
    return render(request, 'events/home.html')


# -----------------------
# Тіркелу (email міндетті)
# -----------------------
def register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email    = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        confirm  = request.POST.get('confirm_password') or ''

        if not username or not email or not password or not confirm:
            messages.error(request, 'Все поля должны быть заполнены!')
            return render(request, 'events/register.html')

        if password != confirm:
            messages.error(request, 'Пароли не совпадают!')
            return render(request, 'events/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует!')
            return render(request, 'events/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Эта почта уже используется!')
            return render(request, 'events/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # тіркелгеннен кейін бірден кіру
        messages.success(request, 'Аккаунт успешно создан! Добро пожаловать.')
        _notify(user, "Добро пожаловать!", "Вы успешно зарегистрировались в системе KINI × Yessenov.")
        return redirect('dashboard')

    return render(request, 'events/register.html')


# -----------------------
# Кіру / Шығу
# -----------------------
def login_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Сәтті кірдіңіз.')
            return redirect('dashboard')
        messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'events/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# -----------------------
# Дашборд (FullCalendar, т.б.)
# -----------------------
@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'events/dashboard.html')


# -----------------------
# Іс-шара құру (тек админ)
# -----------------------
@login_required(login_url='/login/')
def create_event(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Тек админ құра алады.")

    if request.method == 'POST':
        Event.objects.create(
            title=request.POST.get('title', '').strip(),
            description=request.POST.get('description', '').strip(),
            date=request.POST.get('date'),
            time=request.POST.get('time') or None,
            place=request.POST.get('place', '').strip(),
            capacity=int(request.POST.get('capacity') or 100),
            created_by=request.user,
        )
        messages.success(request, 'Мероприятие успешно создано!')
        return redirect('dashboard')

    return render(request, 'events/create_event.html')


# -----------------------
# JSON: Барлық іс-шаралар (календарь үшін)
# -----------------------
@login_required(login_url='/login/')
def events_json(request):
    events = Event.objects.all().order_by('date', 'time')
    data = []
    for e in events:
        # FullCalendar үшін "start" ISO форматта жақсы оқылады
        start = str(e.date)
        if e.time:
            start = f"{e.date}T{e.time}"
        data.append({
            'id': e.id,
            'title': e.title,
            'start': start,
            'extendedProps': {
                'place': e.place,
                'description': e.description,
                'capacity': e.capacity,
                'taken': e.registered_count(),
                'is_full': e.is_full(),
            }
        })
    return JsonResponse(data, safe=False)


# -----------------------
# JSON: Менің тіркелгенім
# -----------------------
@login_required(login_url='/login/')
def my_events_json(request):
    regs = Registration.objects.select_related('event').filter(user=request.user).order_by('-created_at')
    data = []
    for r in regs:
        e = r.event
        start = str(e.date)
        if e.time:
            start = f"{e.date}T{e.time}"
        data.append({
            'id': e.id,
            'title': e.title,
            'start': start,
            'place': e.place,
            'registered_at': r.created_at.isoformat(timespec='seconds'),
        })
    return JsonResponse(data, safe=False)


# -----------------------
# JSON: Хабарламалар
# -----------------------
@login_required(login_url='/login/')
def notifications_json(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    data = [{'id': n.id, 'title': n.title, 'body': n.body,
             'is_read': n.is_read, 'created_at': n.created_at.isoformat(timespec='seconds')}
            for n in notes]
    return JsonResponse(data, safe=False)


# -----------------------
# Тіркелу әрекеті (батырма)
# -----------------------
@login_required(login_url='/login/')
@require_POST
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.is_full():
        return JsonResponse({'ok': False, 'error': 'Мест нет'}, status=400)

    obj, created = Registration.objects.get_or_create(user=request.user, event=event)
    if created:
        _notify(request.user,
                f"Вы записались: {event.title}",
                f"Дата: {event.date} {event.time or ''} • Место: {event.place}")
        return JsonResponse({'ok': True, 'message': 'Вы успешно записались.'})
    else:
        return JsonResponse({'ok': False, 'error': 'Вы уже записаны.'}, status=400)