from django.urls import path
from . import views

app_name = 'skills_api'

urlpatterns = [
    path('gap/', views.gap_analysis, name='gap'),
]
