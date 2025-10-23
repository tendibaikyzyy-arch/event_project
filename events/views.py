from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from .models import Event


# 🏠 Басты бет (home)
def home(request):
    return render(request, 'events/home.html')


# 🧾 Тіркелу (Register)
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if not username or not password:
            messages.error(request, 'Поля не должны быть пустыми!')
            return render(request, 'events/register.html')

        if password != confirm:
            messages.error(request, 'Пароли не совпадают!')
            return render(request, 'events/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует!')
            return render(request, 'events/register.html')

        # ✅ Пользовательді құру
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Аккаунт успешно создан!')

        # ✅ Тіркелген соң логин бетке бағыттау
        return redirect('login')

    return render(request, 'events/register.html')


# 🔐 Кіру (Login)
from django.urls import reverse

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # ✅ Сохраняем сессию явно
            request.session['user_id'] = user.id
            request.session.modified = True

            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard')   # ← переход в календарь
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'events/login.html')


# 🚪 Шығу (Logout)
def logout_view(request):
    logout(request)
    return redirect('login')


# 📅 Dashboard (Календарь)
@login_required(login_url='/login/')
def dashboard(request):
    print("DASHBOARD VIEW WORKING ✅")
    return render(request, 'events/dashboard.html')


# 🛠️ Тек админге арналған — Мероприятие қосу
@login_required(login_url='login')
def create_event(request):
    if not request.user.is_superuser:  # 🔒 тек админге рұқсат
        return redirect('dashboard')

    if request.method == 'POST':
        Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            date=request.POST['date'],
            time=request.POST.get('time', '00:00'),
            place=request.POST.get('location', ''),
            created_by=request.user,
        )
        messages.success(request, 'Мероприятие успешно создано!')
        return redirect('dashboard')

    return render(request, 'events/create_event.html')


# 📦 JSON форматтағы іс-шаралар (календарь үшін)
@login_required(login_url='login')
def events_json(request):
    events = Event.objects.all()
    data = []
    for e in events:
        data.append({
            'title': e.title,
            'start': str(e.date),
            'description': e.description,
        })
    return JsonResponse(data, safe=False)