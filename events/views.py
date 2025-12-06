# events/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Avg

from .models import Event, Registration, Notification


# ---------------------------
# Басты бет
# ---------------------------
def home(request):
    return render(request, 'events/home.html')


# ---------------------------
# Тіркелу (email міндетті)
# ---------------------------
def register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email    = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        confirm  = request.POST.get('confirm_password') or ''

        if not username or not email or not password:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'events/register.html')

        if password != confirm:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'events/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'events/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Эта почта уже используется.')
            return render(request, 'events/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        # Сразу логиним и кидаем на дашборд
        login(request, user)
        messages.success(request, 'Аккаунт создан. Добро пожаловать!')
        return redirect('dashboard')

    return render(request, 'events/register.html')


# ---------------------------
# Кіру / Шығу
# ---------------------------
def login_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'events/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------
# Дашборд (бір бетте 4 вкладка)
# ---------------------------
@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'events/dashboard.html')


# ---------------------------
# Тек админге: іс-шара жасау
# ---------------------------
@login_required(login_url='/login/')
def create_event(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Только админ может создавать события.')

    if request.method == 'POST':
        title = request.POST.get('title') or ''
        description = request.POST.get('description') or ''
        date = request.POST.get('date')  # YYYY-MM-DD
        time = request.POST.get('time')  # HH:MM
        place = request.POST.get('location') or ''
        capacity = int(request.POST.get('capacity') or 100)

        Event.objects.create(
            title=title,
            description=description,
            date=date,
            time=time or None,
            place=place,
            capacity=capacity,
            created_by=request.user,
        )
        messages.success(request, 'Мероприятие создано.')
        return redirect('dashboard')

    return render(request, 'events/create_event.html')


# ---------------------------
# API: барлық іс-шаралар (календарь және “Мероприятия” үшін)
# ---------------------------
@login_required(login_url='/login/')
def events_json(request):
    events = Event.objects.all().order_by('date', 'time')
    data = []
    for e in events:
        start = f"{e.date}T{(e.time or '00:00')}"
        data.append({
            'id': e.id,
            'title': e.title,
            'start': start,
            'description': e.description,
            'place': e.place,
            'capacity': e.capacity,
            'taken': e.registered_count(),
        })
    return JsonResponse(data, safe=False)


# ---------------------------
# API: “Мои события”
# ---------------------------
@login_required(login_url='/login/')
def my_events_json(request):
    regs = Registration.objects.select_related('event').filter(user=request.user).order_by('created_at')
    data = []
    for r in regs:
        e = r.event
        data.append({
            'id': e.id,
            'title': e.title,
            'date': str(e.date),
            'time': str(e.time) if e.time else '',
            'place': e.place,
        })
    return JsonResponse(data, safe=False)


# ---------------------------
# API: уведомления (список)
# ---------------------------
@login_required(login_url='/login/')
def notifications_json(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:100]
    data = []
    for n in notes:
        data.append({
            'id': n.id,
            'title': n.title,
            'body': n.body,
            'created': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': n.is_read,
        })

    # всё, что было непрочитанным, считаем прочитанным
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return JsonResponse(data, safe=False)


# ---------------------------
# API: количество непрочитанных уведомлений
# ---------------------------
@login_required(login_url='/login/')
def notifications_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread': count})


# ---------------------------
# Запись на мероприятие (кнопка “Записаться”)
# ---------------------------
@login_required(login_url='/login/')
def register_for_event(request, event_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Только POST')

    event = get_object_or_404(Event, id=event_id)

    # Проверка мест
    if event.is_full():
        messages.error(request, 'Свободных мест нет.')
        return redirect('dashboard')

    try:
        Registration.objects.create(user=request.user, event=event)
    except IntegrityError:
        # уже записан
        messages.info(request, 'Вы уже зарегистрированы на это мероприятие.')
        return redirect('dashboard')

    # 1) Уведомление СТУДЕНТУ
    Notification.objects.create(
        user=request.user,
        title='Успешная регистрация',
        body=f'Вы записались на «{event.title}» ({event.date} {event.time or ""})'
    )

    # 2) Уведомление ОРГАНИЗАТОРУ (created_by),
    #    если он указан и это не тот же самый человек
    if event.created_by and event.created_by != request.user:
        Notification.objects.create(
            user=event.created_by,
            title='Новая регистрация на ваше мероприятие',
            body=f'Пользователь {request.user.username} записался на «{event.title}» '
                 f'({event.date} {event.time or ""}).'
        )

    messages.success(request, 'Вы записаны! Событие появится во вкладке “Мои события”.')
    return redirect('dashboard')

# ---------------------------
# Отчёты для администратора
# ---------------------------
@login_required
def reports(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Тек администраторлар көре алады.")

    # Барлық event-терді аламыз
    events = Event.objects.all().order_by("date")

    # Әр event үшін статистика жасаймыз
    data = []
    for e in events:
        total = e.registered_count()   # қанша тіркелді
        # attendance кейін қосамыз (қазір None)
        data.append({
            "title": e.title,
            "date": e.date,
            "registered": total,
            "attendance": "—",  # кейін функция жасаймыз
        })

    return render(request, "events/reports.html", {"events": data})