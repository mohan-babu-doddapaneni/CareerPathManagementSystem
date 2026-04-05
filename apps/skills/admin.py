from django.contrib import admin
from .models import OccupationRole, RequiredSkill, SkillGapReport


class RequiredSkillInline(admin.TabularInline):
    model = RequiredSkill
    extra = 0


@admin.register(OccupationRole)
class OccupationRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'onet_code', 'source', 'updated_at']
    inlines = [RequiredSkillInline]


@admin.register(SkillGapReport)
class SkillGapReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'match_percentage', 'generated_at']
    list_filter = ['role']
