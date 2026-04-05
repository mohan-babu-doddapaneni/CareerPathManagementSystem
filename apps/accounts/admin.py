from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'years_experience', 'created_at']
    list_filter = ['target_role']
    search_fields = ['user__email', 'user__first_name']
