from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('resume_upload', 'Resume Upload'),
        ('job_search', 'Job Search'),
        ('job_view', 'Job View'),
        ('ml_predict', 'Career AI Prediction'),
        ('profile_view', 'Profile View'),
        ('skill_add', 'Skill Added'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    detail = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.created_at:%Y-%m-%d %H:%M}"
