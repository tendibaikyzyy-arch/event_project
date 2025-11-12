# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                         # если нужна главная
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # список/деталь/запись (серверные страницы — если пригодятся отдельно)
    path('events/', views.events_list, name='events_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/book/', views.book_event, name='book_event'),

    path('my-events/', views.my_events, name='my_events'),
    path('notifications/', views.notifications, name='notifications'),

    # JSON для SPA-вкладок в dashboard (календарь/списки/уведомления)
    path('events-json/', views.events_json, name='events_json'),
    path('my-events-json/', views.my_events_json, name='my_events_json'),
    path('notifications-json/', views.notifications_json, name='notifications_json'),
    path('create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
]