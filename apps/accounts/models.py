from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    target_role = models.ForeignKey(
        'skills.OccupationRole',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='targeting_users'
    )
    years_experience = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.email})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.email.split('@')[0]

    @property
    def profile_completion(self):
        """Returns 0–100 integer representing how complete the profile is."""
        score = 0
        if self.user.first_name:
            score += 15
        if self.phone:
            score += 10
        if self.target_role:
            score += 15
        try:
            resume = self.user.resume
            if resume.skills.exists():
                score += 25
            if resume.education.exists():
                score += 15
            if resume.experiences.exists():
                score += 20
        except Exception:
            pass
        return min(score, 100)
