from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Registration
from .forms import EventForm


# 🔹 Главная страница
def home(request):
    return render(request, 'events/home.html')


# 🔹 Вход
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
    event = Event.objects.get(id=event_id)
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'Вы уже зарегистрированы!')
    elif Registration.objects.filter(event=event).count() >= event.capacity:
        messages.error(request, 'Мест больше нет 😢')
    else:
        Registration.objects.create(event=event, user=request.user)
        messages.success(request, 'Вы успешно зарегистрировались!')
    return redirect('events_list')


@login_required
def dashboard(request):
    """
    Личный кабинет с календарём.
    Сначала пытаемся взять события из БД (Event),
    если модели/данных нет — показываем примеры.
    """
    import json
    import datetime

    events_payload = []
    try:
        from .models import Event
        qs = Event.objects.order_by('date')[:200]
        for e in qs:
            t = getattr(e, 'time', None) or datetime.time(18, 0)
            start_iso = datetime.datetime.combine(e.date, t).isoformat()
            events_payload.append({
                "id": e.id,
                "title": e.title,
                "start": start_iso,
                "extendedProps": {"place": getattr(e, 'place', '')},
            })
    except Exception:
        # Демонстрационные события (если модели ещё нет)
        events_payload = [
            {"id": 1, "title": "Осенний бал", "start": "2025-10-16T18:00:00", "extendedProps":{"place":"Актовый зал"}},
            {"id": 2, "title": "Хэллоуин", "start": "2025-10-31T19:00:00", "extendedProps":{"place":"Студклуб"}},
            {"id": 3, "title": "Встреча с деканом", "start": "2025-10-20T15:00:00", "extendedProps":{"place":"Актовый зал"}},
            {"id": 4, "title": "Кинозал", "start": "2025-10-22T20:00:00", "extendedProps":{"place":"Кинозал"}},
        ]

    return render(request, "events/dashboard.html", {
        "events_json": json.dumps(events_payload, ensure_ascii=False)
    })