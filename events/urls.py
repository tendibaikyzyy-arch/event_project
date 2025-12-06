# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # auth
    path('login/',    views.login_view,  name='login'),
    path('register/', views.register,    name='register'),
    path('logout/',   views.logout_view, name='logout'),

    # dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # JSON APIs
    path('events-json/',        views.events_json,        name='events_json'),
    path('my-events-json/',     views.my_events_json,     name='my_events_json'),
    path('notifications-json/', views.notifications_json, name='notifications_json'),
    path('notifications-unread-count/',
         views.notifications_unread_count,
         name='notifications_unread_count'),

    # запись на событие
    path('events/<int:event_id>/book/',
         views.register_for_event,
         name='register_for_event'),

    # отчёты
    path('reports/', views.reports, name='reports'),

    # отзывы
    path('events/<int:event_id>/feedback/',
         views.leave_feedback,
         name='leave_feedback'),

    path('feedbacks/',          # <— БЕЗ id
         views.feedback_list,
         name='feedback_list'),
]