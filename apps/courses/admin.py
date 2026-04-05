from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'difficulty', 'is_free', 'rating', 'duration_hours']
    list_filter = ['platform', 'difficulty', 'is_free']
    search_fields = ['title', 'skill_tags']
