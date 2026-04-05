from django.db import models
from django.conf import settings


class OccupationRole(models.Model):
    SOURCE_CHOICES = [('csv', 'CSV Seed'), ('onet', 'O*NET API')]

    name = models.CharField(max_length=200, unique=True)
    onet_code = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='csv')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class RequiredSkill(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skill'),
        ('advanced', 'Advanced Concept'),
        ('certification', 'Certification'),
    ]
    role = models.ForeignKey(OccupationRole, on_delete=models.CASCADE, related_name='required_skills')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='technical')
    importance = models.PositiveSmallIntegerField(default=50)

    class Meta:
        unique_together = ('role', 'name')
        ordering = ['-importance', 'name']

    def __str__(self):
        return f"{self.name} ({self.role.name})"


class SkillGapReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gap_reports'
    )
    role = models.ForeignKey(OccupationRole, on_delete=models.CASCADE)
    match_percentage = models.FloatField(default=0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    missing_certifications = models.JSONField(default=list)
    missing_advanced = models.JSONField(default=list)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.email} → {self.role.name} ({self.match_percentage:.0f}%)"
