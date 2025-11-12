from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import Event, Registration, Notification

# ---- util ----
def _notify(user, title, body=""):
    try:
        Notification.objects.create(user=user, title=title, body=body)
    except Exception:
        pass

# ---- auth ----
def home(request):
    return render(request, 'events/home.html')

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
        login(request, user)
        messages.success(request, 'Аккаунт успешно создан!')
        _notify(user, "Добро пожаловать!", "Вы успешно зарегистрировались в системе.")
        return redirect('dashboard')
    return render(request, 'events/register.html')

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

# ---- dashboard pages ----
@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'events/dashboard.html')

@login_required(login_url='/login/')
def events_list(request):
    events = Event.objects.all().order_by('date', 'time')
    return render(request, 'events/events_list.html', {'events': events})

@login_required(login_url='/login/')
def my_events(request):
    regs = Registration.objects.select_related('event').filter(user=request.user).order_by('-created_at')
    return render(request, 'events/my_events.html', {'regs': regs})

@login_required(login_url='/login/')
def notifications_view(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')[:100]
    return render(request, 'events/notifications.html', {'notes': notes})

# ---- actions / json ----
@login_required(login_url='/login/')
@require_POST
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.is_full():
        messages.error(request, 'К сожалению, мест нет.')
        return redirect('events_list')
    reg, created = Registration.objects.get_or_create(user=request.user, event=event)
    if created:
        messages.success(request, 'Вы записались на мероприятие.')
        _notify(request.user, f"Запись подтверждена: {event.title}",
                f"Дата: {event.date} {event.time or ''} • Место: {event.place}")
    else:
        messages.info(request, 'Вы уже были записаны на это мероприятие.')
    return redirect('my_events')

@login_required(login_url='/login/')
def events_json(request):
    data = []
    for e in Event.objects.all():
        start = str(e.date) if not e.time else f"{e.date}T{e.time}"
        data.append({'id': e.id, 'title': e.title, 'start': start})
    return JsonResponse(data, safe=False)