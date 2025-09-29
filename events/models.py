from django.db import models
from django.contrib.auth.models import User

# Мероприятия моделі
class Event(models.Model):
    title = models.CharField(max_length=200)              # атауы
    description = models.TextField()                      # сипаттама
    date = models.DateField()                             # дата
    location = models.CharField(max_length=200)           # орын
    capacity = models.IntegerField(default=100)           # орын саны

    def __str__(self):
        return self.title

# Қатысушылар тізімі
class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

# Кері байланыс (отзывы)
class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(default=5)
    timestamp = models.DateTimeField(auto_now_add=True)