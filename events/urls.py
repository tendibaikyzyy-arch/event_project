from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # аутентификация
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # дэшборд
    path('dashboard/', views.dashboard, name='dashboard'),

    # создание события (только админ)
    path('create/', views.create_event, name='create_event'),

    # JSON API
    path('events-json/', views.events_json, name='events_json'),
    path('my-events-json/', views.my_events_json, name='my_events_json'),
    path('notifications-json/', views.notifications_json, name='notifications_json'),

    # запись на событие (POST)
    path('events/<int:event_id>/book/', views.register_for_event, name='register_for_event'),
]