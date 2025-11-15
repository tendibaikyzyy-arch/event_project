from django.conf import settings
from django.db import models


class Event(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date        = models.DateField()
    time        = models.TimeField(null=True, blank=True)
    place       = models.CharField(max_length=200, blank=True)
    capacity    = models.PositiveIntegerField(default=100)

    # Админ өшірілсе, шара жоғалып кетпесін:
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events_created"
    )

    class Meta:
        ordering = ["date", "time"]  # тізімдер мен календарьға ыңғайлы

    def __str__(self):
        return f"{self.title} — {self.date}"

    # 👉 views.py осыны қолданады
    def registered_count(self) -> int:
        return self.registrations.count()

    def is_full(self) -> bool:
        return self.registered_count() >= self.capacity


class Registration(models.Model):
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")    # бір user бір event-ке бір-ақ рет
        indexes = [models.Index(fields=["user", "event"])]

    def __str__(self):
        return f"{self.user} → {self.event.title}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=200)
    body  = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notify({self.user}): {self.title[:30]}"