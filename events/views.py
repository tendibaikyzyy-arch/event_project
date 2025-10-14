from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# 🔹 Басты бет
def home(request):
    return render(request, 'events/home.html')

# 🔹 Кіру
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Қош келдің, {username}! 🌸")
            return redirect('home')
        else:
            messages.error(request, "Қате логин немесе пароль 😢")

    return render(request, 'events/login.html')

# 🔹 Тіркелу
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Құпиясөздер сәйкес емес ❌")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Бұл логин бос емес ⚠️")
            return redirect('signup')

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Тіркелу сәтті өтті ✅ Енді кіріңіз!")
        return redirect('login')

    return render(request, 'events/login.html')