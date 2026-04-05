from django.db import models
from django.utils import timezone


class JobListing(models.Model):
    adzuna_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=10, default='us')
    description = models.TextField(blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    redirect_url = models.URLField()
    category = models.CharField(max_length=200, blank=True)
    skill_tags = models.JSONField(default=list)
    matched_role = models.ForeignKey(
        'skills.OccupationRole',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='job_listings'
    )
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['country', 'category']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['matched_role']),
        ]
        ordering = ['-fetched_at']

    def __str__(self):
        return f"{self.title} @ {self.company}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} – ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"${self.salary_min:,.0f}+"
        return None
