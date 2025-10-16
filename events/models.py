from django.db import models
from django.contrib.auth.models import User

# 🔹 Модель мероприятия
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    place = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=50)  # лимит участников

    def __str__(self):
        return self.title


# 🔹 Модель регистрации на мероприятие
class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_registered = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')  # нельзя дважды записаться

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"