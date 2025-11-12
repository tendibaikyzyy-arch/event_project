from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # аутентификация
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # дашборд беттері
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/events/', views.events_list, name='events_list'),
    path('dashboard/my-events/', views.my_events, name='my_events'),
    path('dashboard/notifications/', views.notifications_view, name='notifications'),

    # әрекеттер/JSON
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events-json/', views.events_json, name='events_json'),
]