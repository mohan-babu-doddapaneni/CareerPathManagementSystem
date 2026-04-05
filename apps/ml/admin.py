from django.contrib import admin
from .models import JobDataset, TrainedModel, ModelPerformance


@admin.register(JobDataset)
class JobDatasetAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'predicted_job_title', 'industry', 'years_of_experience', 'education_level']
    search_fields = ['job_id', 'predicted_job_title']


@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ['algorithm', 'is_active', 'trained_at']
    list_filter = ['algorithm', 'is_active']
    actions = ['set_active']

    def set_active(self, request, queryset):
        for obj in queryset:
            obj.is_active = True
            obj.save()
    set_active.short_description = 'Set selected models as active'


@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['model', 'accuracy', 'precision', 'recall', 'f1_score', 'training_samples']
