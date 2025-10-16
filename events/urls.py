from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-events/', views.my_events_view, name='my_events'),
    path('notifications/', views.notifications_view, name='notifications'),
]