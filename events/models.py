from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    place = models.CharField(max_length=150)
    capacity = models.PositiveIntegerField(default=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')

    def __str__(self):
        return self.title


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"