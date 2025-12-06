from django.contrib import admin
from .models import Event, Registration, Notification


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "place", "capacity", "created_by")
    readonly_fields = ("created_by",)

    def save_model(self, request, obj, form, change):
        # Егер жаңа event болса немесе created_by бос болса – автоматты түрде орнатамыз
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")