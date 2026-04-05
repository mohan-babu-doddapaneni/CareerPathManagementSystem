from django.urls import path
from . import views
from apps.accounts import views as account_views
from apps.resumes import views as resume_views
from apps.skills import views as skill_views
from apps.jobs import views as job_views
from apps.ml import views as ml_views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health, name='health'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Accounts
    path('profile/', account_views.profile, name='profile'),
    path('profile/update/', account_views.update_profile, name='update_profile'),

    # Resumes
    path('resume/', resume_views.resume_page, name='resume'),
    path('resume/upload/', resume_views.upload_resume, name='upload_resume'),
    path('resume/delete/', resume_views.delete_resume, name='delete_resume'),
    path('resume/skill/add/', resume_views.add_skill, name='add_skill'),
    path('resume/skill/<int:pk>/delete/', resume_views.delete_skill, name='delete_skill'),
    path('resume/education/add/', resume_views.add_education, name='add_education'),
    path('resume/education/<int:pk>/delete/', resume_views.delete_education, name='delete_education'),
    path('resume/experience/add/', resume_views.add_experience, name='add_experience'),
    path('resume/experience/<int:pk>/delete/', resume_views.delete_experience, name='delete_experience'),
    path('resume/certification/add/', resume_views.add_certification, name='add_certification'),
    path('resume/certification/<int:pk>/delete/', resume_views.delete_certification, name='delete_certification'),

    # Skills
    path('skills/analyse/', skill_views.analyse_page, name='analyse'),
    path('skills/gap/', skill_views.gap_analysis, name='gap_analysis'),
    path('skills/predict/', skill_views.predict_role, name='predict_role'),

    # Jobs
    path('jobs/', job_views.job_board, name='jobs'),
    path('jobs/<int:pk>/', job_views.job_detail, name='job_detail'),

    # ML
    path('ml/', ml_views.ml_dashboard, name='ml_dashboard'),
    path('ml/predict/', ml_views.prediction_form, name='prediction_form'),
    path('ml/train/<str:algorithm>/', ml_views.train_model_view, name='train_model'),
]
