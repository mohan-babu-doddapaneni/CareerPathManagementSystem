from django.db import models


class Course(models.Model):
    PLATFORM_CHOICES = [
        ('coursera', 'Coursera'),
        ('udemy', 'Udemy'),
        ('youtube', 'YouTube'),
        ('freecodecamp', 'freeCodeCamp'),
        ('edx', 'edX'),
        ('linkedin', 'LinkedIn Learning'),
        ('pluralsight', 'Pluralsight'),
        ('kaggle', 'Kaggle'),
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('other', 'Other'),
    ]
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=300)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField(max_length=500)
    skill_tags = models.CharField(max_length=500, help_text='Comma-separated skill names this course covers')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.PositiveSmallIntegerField(default=0, help_text='Estimated hours to complete')
    is_free = models.BooleanField(default=True)
    rating = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', 'title']
        indexes = [
            models.Index(fields=['skill_tags']),
            models.Index(fields=['platform']),
        ]

    def __str__(self):
        return f"[{self.platform}] {self.title}"

    def skill_list(self):
        return [s.strip().lower() for s in self.skill_tags.split(',') if s.strip()]

    def platform_color(self):
        colors = {
            'coursera': 'blue',
            'udemy': 'purple',
            'youtube': 'red',
            'freecodecamp': 'green',
            'edx': 'indigo',
            'kaggle': 'cyan',
            'google': 'yellow',
            'microsoft': 'sky',
            'linkedin': 'blue',
        }
        return colors.get(self.platform, 'gray')
