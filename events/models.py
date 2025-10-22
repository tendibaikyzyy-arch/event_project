from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField("Название мероприятия", max_length=100)
    description = models.TextField("Описание", blank=True)
    date = models.DateField("Дата проведения")
    time = models.TimeField("Время проведения")
    place = models.CharField("Место проведения", max_length=100)
    capacity = models.PositiveIntegerField("Вместимость", default=50)
    created_by = models.ForeignKey(User, verbose_name="Создано пользователем", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} — {self.date}"

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"


class Registration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='registrations', on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"

    def __str__(self):
        return f"{self.user.username} зарегистрирован на {self.event.title}"