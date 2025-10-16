from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.register_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
]