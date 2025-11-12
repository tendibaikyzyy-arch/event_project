# eventsystem/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # fallback login view (қажет болса)
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='events/login.html'),
        name='account_login'
    ),

    # барлық маршруттар events ішінен
    path('', include('events.urls')),
]