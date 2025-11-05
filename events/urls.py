from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_event, name='create_event'),
    path('events-json/', views.events_json, name='events_json'),
    path('events/<int:event_id>/signup/', views.event_signup, name='event_signup'),
    path('my-events/', views.my_events, name='my_events'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.notification_read, name='notif_read'),
]