from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages   # ✅ МІНДЕТТІ
from .models import Event

def home(request):
    return render(request, 'events/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  # ← осылай болу керек
        confirm = request.POST.get('confirm_password')  # егер бар болса
        
        if not username or not password:
            messages.error(request, "Поля не должны быть пустыми!")
            return render(request, 'events/register.html')

        if password != confirm:
            messages.error(request, "Пароли не совпадают!")
            return render(request, 'events/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует!")
            return render(request, 'events/register.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Аккаунт успешно создан!")
        return redirect('login')

    return render(request, 'events/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'events/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    # Тек календарь көрсетіледі
    return render(request, 'events/dashboard.html')

@login_required
def create_event(request):
    if not request.user.is_superuser:
        return redirect('dashboard')  # 🔒 Тек админге рұқсат
    if request.method == 'POST':
        Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            date=request.POST['date'],
            location=request.POST['location'],
            created_by=request.user
        )
        return redirect('dashboard')
    return render(request, 'events/create_event.html')

@login_required
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