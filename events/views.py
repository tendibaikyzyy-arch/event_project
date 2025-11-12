from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Event, Registration, Notification

# --- JSON: все события для календаря и списка ---
@login_required(login_url='/login/')
def events_json(request):
    events = (
        Event.objects
        .select_related('created_by')
        .order_by('date', 'time')
    )

    data = []
    for e in events:
        # ISO "start" для FullCalendar и для списка
        start = str(e.date)
        if e.time:
            start = f"{e.date}T{e.time}"

        data.append({
            "id": e.id,
            "title": e.title,
            "description": e.description or "",
            "start": start,
            "place": e.place or "",
            "capacity": e.capacity,
            "taken": Registration.objects.filter(event=e).count(),
        })
    return JsonResponse(data, safe=False)

# --- JSON: мои события ---
@login_required(login_url='/login/')
def my_events_json(request):
    regs = (
        Registration.objects
        .filter(user=request.user)
        .select_related('event')
        .order_by('created_at')
    )
    data = []
    for r in regs:
        e = r.event
        data.append({
            "id": e.id,
            "title": e.title,
            "date": str(e.date),
            "time": str(e.time) if e.time else "",
            "place": e.place or "",
        })
    return JsonResponse(data, safe=False)

# --- JSON: уведомления пользователя ---
@login_required(login_url='/login/')
def notifications_json(request):
    notes = (
        Notification.objects
        .filter(user=request.user)
        .order_by('-created_at')[:100]
    )
    data = []
    for n in notes:
        data.append({
            "id": n.id,
            "title": n.title,
            "body": n.body or "",
            "created": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_read": n.is_read,
        })
    return JsonResponse(data, safe=False)

# --- POST: записаться на событие ---
@login_required(login_url='/login/')
def register_for_event(request, event_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("POST only")

    event = get_object_or_404(Event, id=event_id)

    # проверка на дубликаты/места
    already = Registration.objects.filter(user=request.user, event=event).exists()
    taken = Registration.objects.filter(event=event).count()
    if already:
        messages.error(request, "Вы уже записаны на это мероприятие.")
        return redirect('dashboard')
    if taken >= event.capacity:
        messages.error(request, "Мест больше нет 😔")
        return redirect('dashboard')

    Registration.objects.create(user=request.user, event=event)

    # создаём локальное уведомление
    Notification.objects.create(
        user=request.user,
        title="Запись подтверждена",
        body=f"Вы записались: «{event.title}» ({event.date}{' '+str(event.time) if event.time else ''}).",
    )

    messages.success(request, "Успешно! Вы записались на мероприятие.")
    return redirect('dashboard')