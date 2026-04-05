from django.contrib import admin
from .models import Resume, ParsedSkill, ParsedEducation, ParsedExperience


class ParsedSkillInline(admin.TabularInline):
    model = ParsedSkill
    extra = 0


class ParsedEducationInline(admin.TabularInline):
    model = ParsedEducation
    extra = 0


class ParsedExperienceInline(admin.TabularInline):
    model = ParsedExperience
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_filename', 'parsed_at', 'created_at']
    inlines = [ParsedSkillInline, ParsedEducationInline, ParsedExperienceInline]
