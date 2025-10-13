from django.contrib import admin
from django.urls import path, include
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # басты бет Home.html-ға сілтейді
    path('events/', include('events.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)