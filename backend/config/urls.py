"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('apps.accounts.admin_urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/timetable/', include('apps.timetable.urls')),
    path('api/scheduler/', include('apps.scheduler.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/study-groups/', include('apps.study_groups.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
