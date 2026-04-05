from django.db import models
from django.conf import settings


class Resume(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume'
    )
    file = models.FileField(upload_to='resumes/', null=True, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    raw_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    linkedin_url = models.URLField(max_length=300, blank=True)
    github_url = models.URLField(max_length=300, blank=True)
    parsed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume({self.user.email})"


class ParsedSkill(models.Model):
    SOURCE_CHOICES = [
        ('parsed', 'Auto-parsed'),
        ('manual', 'Manually added'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='parsed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resume', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class ParsedEducation(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=10, default='parsed')

    class Meta:
        ordering = ['-year', '-id']

    def __str__(self):
        return self.degree


class ParsedExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    duration_text = models.CharField(max_length=100, blank=True)
    years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    source = models.CharField(max_length=10, default='parsed')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class ParsedCertification(models.Model):
    SOURCE_CHOICES = [
        ('parsed', 'Auto-parsed'),
        ('manual', 'Manually added'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=300)
    issuer = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='parsed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resume', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name
