from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def train_model_task(self, algorithm_key):
    try:
        from .classifier import train_model
        _, metrics = train_model(algorithm_key)
        logger.info(f'Trained {algorithm_key}: {metrics}')
        return metrics
    except Exception as e:
        logger.error(f'Training task failed: {e}')
        raise self.retry(exc=e, countdown=60)


@shared_task
def fetch_jobs_for_all_roles():
    """Refresh Adzuna job listings for all roles."""
    from apps.skills.models import OccupationRole
    from apps.jobs.models import JobListing
    from apps.jobs.adzuna import AdzunaClient

    client = AdzunaClient()
    expires = timezone.now() + timedelta(hours=24)
    total = 0

    for role in OccupationRole.objects.all():
        results = client.search(what=role.name, country='us', results=20)
        for raw in results:
            data = client.normalize_job(raw)
            if not data['adzuna_id']:
                continue
            JobListing.objects.update_or_create(
                adzuna_id=data['adzuna_id'],
                defaults={**data, 'matched_role': role, 'expires_at': expires}
            )
            total += 1

    logger.info(f'Fetched {total} job listings from Adzuna.')
    return total


@shared_task
def cleanup_expired_jobs():
    """Delete expired job listings."""
    from apps.jobs.models import JobListing
    deleted, _ = JobListing.objects.filter(expires_at__lt=timezone.now()).delete()
    logger.info(f'Deleted {deleted} expired job listings.')
    return deleted
