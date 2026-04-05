from django.urls import path
from . import views

app_name = 'jobs_api'

urlpatterns = [
    path('search/', views.job_search_api, name='search'),
]
