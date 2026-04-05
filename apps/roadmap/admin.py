from django.contrib import admin
from .models import CareerGoal, LearningStep


class LearningStepInline(admin.TabularInline):
    model = LearningStep
    extra = 0
    fields = ['skill_name', 'category', 'order', 'status']


@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'status', 'completion_pct', 'created_at']
    list_filter = ['status', 'target_role']
    inlines = [LearningStepInline]
