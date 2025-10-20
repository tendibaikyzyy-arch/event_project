from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Registration
from .forms import EventForm
import json
import datetime


# 🔹 Главная
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
            messages.success(request, f'Аккаунт создан! Теперь войдите.')
            return redirect('login')
        else:
            messages.error(request, 'Ошибка при регистрации.')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})


# 🔹 Выход
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


# 🔹 Список мероприятий
def events_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/events_list.html', {'events': events})


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
            return redirect('events_list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


# 🔹 Регистрация на мероприятие
@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы!')
    elif Registration.objects.filter(event=event).count() >= event.capacity:
        messages.error(request, 'Мест больше нет 😢')
    else:
        Registration.objects.create(event=event, user=request.user)
        messages.success(request, f'✅ Вы записались на "{event.title}"!')
    return redirect('dashboard')


# 🔹 Мои мероприятия
@login_required
def my_events(request):
    my_regs = Registration.objects.filter(user=request.user)
    return render(request, 'events/my_events.html', {'registrations': my_regs})


# 🔹 Dashboard (главная страница после входа)
@login_required
def dashboard(request):
    events_payload = []
    try:
        events = Event.objects.order_by('date')
        for e in events:
            t = getattr(e, 'time', None) or datetime.time(18, 0)
            start_iso = datetime.datetime.combine(e.date, t).isoformat()
            events_payload.append({
                "id": e.id,
                "title": e.title,
                "start": start_iso,
                "extendedProps": {"place": getattr(e, 'place', '')},
            })
    except:
        events_payload = []

    return render(request, 'events/dashboard.html', {
        "events_json": json.dumps(events_payload, ensure_ascii=False)
    })


# 🔹 Уведомления (позже можно email)
@login_required
def notifications(request):
    return render(request, 'events/notifications.html')