from django.contrib import admin
from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'user', 'status', 'applied_date', 'created_at']
    list_filter = ['status']
    search_fields = ['job_title', 'company', 'user__email']
