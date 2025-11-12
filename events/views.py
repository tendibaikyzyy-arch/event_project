from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from .models import Event, Registration, Notification

# 🏠 Басты бет (Home)
def home(request):
    return render(request, 'events/home.html')


# 🧾 Тіркелу (Register)
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if not username or not password or not email:
            messages.error(request, 'Все поля должны быть заполнены!')
            return render(request, 'events/register.html')

        if password != confirm:
            messages.error(request, 'Пароли не совпадают!')
            return render(request, 'events/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует!')
            return render(request, 'events/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Почта уже используется!')
            return render(request, 'events/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)
        messages.success(request, 'Аккаунт успешно создан!')
        return redirect('dashboard')

    return render(request, 'events/register.html')


# 🔐 Кіру (Login)
def login_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            return redirect('dashboard')
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
    return render(request, 'events/dashboard.html')


# 📋 Барлық іс-шаралардың JSON (FullCalendar + Events list)
@login_required(login_url='/login/')
def events_json(request):
    events = Event.objects.all()
    data = []
    for e in events:
        data.append({
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'start': str(e.date) + ('T' + str(e.time) if e.time else ''),
            'place': e.place,
            'capacity': e.capacity,
            'taken': e.registered_count(),
        })
    return JsonResponse(data, safe=False)


# 🧾 Мероприятиеге жазылу (Book/Register)
@login_required(login_url='/login/')
def book_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if event.is_full():
        messages.error(request, 'К сожалению, все места заняты.')
        return redirect('dashboard')

    reg, created = Registration.objects.get_or_create(user=request.user, event=event)
    if not created:
        messages.warning(request, 'Вы уже зарегистрированы на это мероприятие.')
    else:
        Notification.objects.create(
            user=request.user,
            title=f"Вы записались на '{event.title}'",
            body=f"Дата: {event.date}, Время: {event.time or 'уточняется'}, Место: {event.place}"
        )
        messages.success(request, f"Вы успешно записались на {event.title}!")

    return redirect('dashboard')


# ⭐ Менің оқиғаларым (My Events JSON)
@login_required(login_url='/login/')
def my_events_json(request):
    regs = Registration.objects.filter(user=request.user)
    data = []
    for r in regs:
        data.append({
            'title': r.event.title,
            'date': str(r.event.date),
            'time': str(r.event.time or ''),
            'place': r.event.place,
        })
    return JsonResponse(data, safe=False)


# 🔔 Уведомления JSON
@login_required(login_url='/login/')
def notifications_json(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for n in notifs:
        data.append({
            'title': n.title,
            'body': n.body,
            'created': n.created_at.strftime('%d.%m.%Y %H:%M')
        })
    return JsonResponse(data, safe=False)