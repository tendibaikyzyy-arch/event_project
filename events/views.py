from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Главная страница (только вход и регистрация)
def home(request):
    return (request, 'events/home.html')


# Регистрация
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Пароли не совпадают ❌")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Такой пользователь уже существует ⚠️")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Регистрация успешна! ✅ Теперь войдите.")
        return redirect('login')

    return render(request, 'events/register.html')

# Логин
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')   # после входа → кабинет
        else:
            messages.error(request, "Неверный логин или пароль")
    return render(request, 'events/login.html')


# Личный кабинет (после входа)
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'events/dashboard.html')


# Выход
def logout_view(request):
    logout(request)
    return redirect('home')