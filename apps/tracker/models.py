from django.db import models
from django.conf import settings


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applied', 'Applied'),
        ('phone_screen', 'Phone Screen'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    STATUS_COLORS = {
        'saved': 'gray',
        'applied': 'blue',
        'phone_screen': 'yellow',
        'interview': 'purple',
        'offer': 'green',
        'rejected': 'red',
        'withdrawn': 'gray',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications'
    )
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    job_url = models.URLField(max_length=500, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='saved')
    applied_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Link to seeded job if user clicked from job board
    job_listing = models.ForeignKey(
        'jobs.JobListing', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='applications'
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.job_title} @ {self.company} ({self.get_status_display()})"

    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'gray')
