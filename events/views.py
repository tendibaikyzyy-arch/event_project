from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Event, Registration
from .forms import EventForm
import json, datetime

def home(request):
    return render(request, 'events/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'events/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Теперь войдите.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    try:
        events = Event.objects.all().order_by('date')
        events_payload = [
            {
                "id": e.id,
                "title": e.title,
                "start": datetime.datetime.combine(e.date, e.time).isoformat(),
                "extendedProps": {"place": e.place},
            }
            for e in events
        ]
    except Exception:
        events_payload = [
            {"id": 1, "title": "Осенний бал", "start": "2025-10-20T18:00:00"},
            {"id": 2, "title": "Хэллоуин", "start": "2025-10-31T19:00:00"},
        ]

    return render(request, 'events/dashboard.html', {
        "events_json": json.dumps(events_payload, ensure_ascii=False)
    })

def notifications(request):
    return render(request, 'events/notifications.html')

@login_required
def events_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/events_list.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Мероприятие создано!')
            return redirect('events_list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def register_for_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы на это мероприятие!')
    elif Registration.objects.filter(event=event).count() >= event.capacity:
        messages.error(request, 'Мест больше нет 😢')
    else:
        Registration.objects.create(event=event, user=request.user)
        messages.success(request, f'Вы успешно записались на "{event.title}"!')
    return redirect('dashboard')