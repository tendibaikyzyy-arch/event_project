from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Главная страница
def home(request):
    return render(request, 'events/home.html')

# Вход
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Введите логин и пароль ⚠️")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Добро пожаловать, {username}! 🎉")
            return redirect('home')
        else:
            messages.error(request, "Неверный логин или пароль 😢")
            return redirect('login')

    return render(request, 'events/login.html')

# Регистрация
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not email or not password1:
            messages.error(request, "Заполните все поля ⚠️")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Пароли не совпадают ❌")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Такой логин уже существует ⚠️")
            return redirect('signup')

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Регистрация прошла успешно ✅ Теперь войдите в систему.")
        return redirect('login')

    return render(request, 'events/login.html')