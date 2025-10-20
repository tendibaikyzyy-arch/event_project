from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ✅ Мына жолды қостық

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='events/login.html'), name='account_login'),  # ✅ Фикс
    path('', include('events.urls')),  # Барлық маршруттар events ішінен
]