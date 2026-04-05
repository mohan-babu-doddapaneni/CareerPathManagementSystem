from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/resumes/', include('apps.resumes.urls', namespace='resumes_api')),
    path('api/skills/', include('apps.skills.urls', namespace='skills_api')),
    path('api/jobs/', include(('apps.jobs.urls', 'jobs_api'), namespace='jobs_api')),
    path('api/ml/', include('apps.ml.urls', namespace='ml_api')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
