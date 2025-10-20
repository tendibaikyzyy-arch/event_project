from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Registration
from .forms import EventForm
import json, datetime

# 🔹 Басты бет
def home(request):
    return render(request, 'events/home.html')

# 🔹 Логин
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('dashboard')  # ✅ логиннен кейін calendar бетке бағыттайды
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'events/login.html')

# 🔹 Тіркелу
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт создан! Войдите, чтобы продолжить.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})

# 🔹 Шығу
def logout_view(request):
    logout(request)
    return redirect('home')

# 🔹 Мероприятие тізімі
@login_required
def events_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/events_list.html', {'events': events})

# 🔹 Мероприятие құру
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

# 🔹 Мероприятиеге тіркелу
@login_required
def register_for_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы!')
    else:
        Registration.objects.create(event=event, user=request.user)
        messages.success(request, 'Вы успешно зарегистрировались!')
    return redirect('dashboard')

# 🔹 Интерактивті календарь беті
@login_required
def dashboard(request):
    events_payload = []
    qs = Event.objects.order_by('date')[:100]
    for e in qs:
        t = getattr(e, 'time', None) or datetime.time(18, 0)
        start_iso = datetime.datetime.combine(e.date, t).isoformat()
        events_payload.append({
            "id": e.id,
            "title": e.title,
            "start": start_iso,
            "extendedProps": {"place": getattr(e, 'place', '')},
        })

    return render(request, "events/dashboard.html", {
        "events_json": json.dumps(events_payload, ensure_ascii=False)
    })


# 🔹 Менің тіркелген іс-шараларым
@login_required
def my_events(request):
    my_regs = Registration.objects.filter(user=request.user).select_related('event')
    return render(request, 'events/my_events.html', {'registrations': my_regs})


# 🔹 Уведомления (қарапайым демо)
@login_required
def notifications(request):
    # Уведомленияны әзірге статикалық мысал ретінде көрсетеміз
    notes = [
        {"type": "reminder", "text": "Завтра состоится мероприятие 'Тіл мерекесі' в 14:00."},
        {"type": "info", "text": "Добавлено новое мероприятие: 'Встреча с деканом'."},
        {"type": "warning", "text": "Мероприятие 'Осенний бал' перенесено на 22 октября."},
    ]
    return render(request, 'events/notifications.html', {'notifications': notes})