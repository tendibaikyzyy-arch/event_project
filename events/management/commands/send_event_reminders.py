from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from events.models import Event, Registration, Notification

class Command(BaseCommand):
    help = "Создает in-app уведомления за 5 дней до события"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        target = today + timedelta(days=5)
        events = Event.objects.filter(date=target)
        created_total = 0
        for ev in events:
            regs = Registration.objects.filter(event=ev).select_related('user')
            for r in regs:
                Notification.objects.get_or_create(
                    user=r.user,
                    title='Скоро мероприятие',
                    body=f'{ev.title} через 5 дней — {ev.date} {ev.time or ""} ({ev.place})'
                )
                created_total += 1
        self.stdout.write(self.style.SUCCESS(f'Создано уведомлений: {created_total}'))