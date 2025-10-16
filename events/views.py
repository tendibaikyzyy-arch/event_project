from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# 🔹 Главная страница
def home(request):
    return render(request, 'events/home.html')

# 🔹 Вход (Login)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'events/login.html')

# 🔹 Регистрация (Signup)
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Эта почта уже зарегистрирована')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Регистрация успешна! Теперь войдите.')
            return redirect('login')

    return render(request, 'events/register.html')

# 🔹 Выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('home')