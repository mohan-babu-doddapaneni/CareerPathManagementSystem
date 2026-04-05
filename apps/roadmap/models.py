from django.db import models
from django.conf import settings
from apps.skills.models import OccupationRole


class CareerGoal(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='career_goal',
    )
    target_role = models.ForeignKey(
        OccupationRole,
        on_delete=models.SET_NULL,
        null=True,
        related_name='career_goals',
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Career Goal'

    def __str__(self):
        return f"{self.user.email} → {self.target_role}"

    def completion_pct(self):
        total = self.steps.count()
        if total == 0:
            return 0
        done = self.steps.filter(status='done').count()
        return round(done / total * 100)


class LearningStep(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Not Started'),
        ('learning', 'In Progress'),
        ('done', 'Completed'),
    ]
    CATEGORY_CHOICES = [
        ('technical', 'Technical Skill'),
        ('soft', 'Soft Skill'),
        ('certification', 'Certification'),
        ('advanced', 'Advanced Concept'),
    ]
    goal = models.ForeignKey(CareerGoal, on_delete=models.CASCADE, related_name='steps')
    skill_name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='technical')
    order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'skill_name']

    def __str__(self):
        return f"{self.skill_name} ({self.get_status_display()})"
