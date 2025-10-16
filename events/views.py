 from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Registration
from .forms import EventForm
import json
import datetime


# 🔹 Главная страница
def home(request):
    return render(request, 'events/home.html')


# 🔹 Вход (авторизация)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'events/login.html')


# 🔹 Регистрация
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан: {username}! Теперь войдите.')
            return redirect('login')
        else:
            messages.error(request, 'Ошибка при регистрации. Попробуйте снова.')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})


# 🔹 Выход
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


# 🔹 Страница после входа — Панель с календарём
@login_required
def dashboard(request):
    events_payload = []

    try:
        # Если есть реальные события в БД
        qs = Event.objects.all().order_by('date')
        for e in qs:
            t = getattr(e, 'time', datetime.time(18, 0))
            start_iso = datetime.datetime.combine(e.date, t).isoformat()
            events_payload.append({
                "id": e.id,
                "title": e.title,
                "start": start_iso,
                "extendedProps": {"place": getattr(e, 'place', '—')}
            })
    except Exception:
        # Демонстрационные (если БД ещё пустая)
        events_payload = [
            {"id": 1, "title": "Осенний бал 🍁", "start": "2025-10-25T18:00:00", "extendedProps": {"place": "Актовый зал"}},
            {"id": 2, "title": "Кинопоказ 🎬", "start": "2025-10-30T19:00:00", "extendedProps": {"place": "Кинозал"}},
            {"id": 3, "title": "Встреча с деканом 🎓", "start": "2025-10-28T16:00:00", "extendedProps": {"place": "Аудитория 201"}},
        ]

    return render(request, "events/dashboard.html", {
        "events_json": json.dumps(events_payload, ensure_ascii=False)
    })


# 🔹 Создание мероприятия
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Мероприятие успешно создано!')
            return redirect('dashboard')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


# 🔹 Список всех мероприятий
@login_required
def events_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/events_list.html', {'events': events})


# 🔹 Регистрация на мероприятие
@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы!')
    elif Registration.objects.filter(event=event).count() >= event.capacity:
        messages.error(request, 'Мест больше нет 😢')
    else:
        Registration.objects.
create(event=event, user=request.user)
        messages.success(request, 'Вы успешно зарегистрировались!')
    return redirect('dashboard')


# 🔹 Страница "Мои записи"
@login_required
def my_events_view(request):
    my_regs = Registration.objects.filter(user=request.user).select_related('event')
    return render(request, 'events/my_events.html', {'registrations': my_regs})


# 🔹 Страница "Уведомления"
@login_required
def notifications_view(request):
    fake_notifs = [
        {"title": "Осенний бал 🍁 уже завтра!", "desc": "Не забудьте костюм и билет 🎟"},
        {"title": "Кинопоказ 🎬 перенесён", "desc": "Новая дата: 30 октября в 19:00."},
    ]
    return render(request, 'events/notifications.html', {'notifications': fake_notifs})