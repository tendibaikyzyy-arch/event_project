# eventsystem/urls.py
from django.contrib import admin
from django.urls import path, include
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),           # твоя главная (баннеры/карточки)
    path('events/', include('events.urls')),     # если есть
    path('dashboard/', views.dashboard, name='dashboard'),  # ЛК с календарём
]