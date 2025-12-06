from django.contrib import admin
from .models import Event, Registration, Notification, Feedback


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "place", "capacity", "created_by")
    list_filter = ("date", "place", "created_by")
    search_fields = ("title", "description")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "created_at", "attended", "rating")
    list_filter = ("attended", "event")
    search_fields = ("user__username", "event__title")
    list_editable = ("attended", "rating")  # можно менять прямо в списке
    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "rating", "created_at")
    list_filter = ("event", "rating")
    search_fields = ("comment", "reply", "user__username")