from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events-list/', views.events_list, name='events_list'),
    path('create/', views.create_event, name='create_event'),
    path('register-event/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('notifications/', views.notifications, name='notifications'),
]