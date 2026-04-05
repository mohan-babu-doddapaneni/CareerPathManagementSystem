from django.db import models


class JobDataset(models.Model):
    job_id = models.CharField(max_length=20, unique=True)
    skills = models.TextField()
    years_of_experience = models.PositiveSmallIntegerField()
    predicted_job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True)
    company_location = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    salary_usd = models.PositiveIntegerField(default=0)
    education_level = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['job_id']

    def __str__(self):
        return f"{self.job_id}: {self.predicted_job_title}"


class TrainedModel(models.Model):
    ALGORITHM_CHOICES = [
        ('random_forest', 'Random Forest'),
        ('naive_bayes', 'Naive Bayes'),
        ('svm', 'SVM (LinearSVC)'),
        ('neural_net', 'Neural Network (MLP)'),
    ]
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES)
    artifact = models.BinaryField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']

    def __str__(self):
        return f"{self.get_algorithm_display()} ({'active' if self.is_active else 'inactive'})"

    def save(self, *args, **kwargs):
        if self.is_active:
            TrainedModel.objects.filter(algorithm=self.algorithm).update(is_active=False)
        super().save(*args, **kwargs)


class ModelPerformance(models.Model):
    model = models.OneToOneField(TrainedModel, on_delete=models.CASCADE, related_name='performance')
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    training_samples = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.model} — Acc:{self.accuracy:.2f}"
