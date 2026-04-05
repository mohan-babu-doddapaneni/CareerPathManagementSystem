from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import JobListing
from .adzuna import AdzunaClient
from apps.skills.models import OccupationRole
import logging

logger = logging.getLogger(__name__)


def _try_adzuna_refresh(role):
    """Silently try to fetch fresh jobs from Adzuna. Never raises."""
    try:
        from django.conf import settings
        if not getattr(settings, 'ADZUNA_APP_ID', '') or not getattr(settings, 'ADZUNA_APP_KEY', ''):
            return  # API keys not configured, skip silently
        from datetime import timedelta
        client = AdzunaClient()
        results = client.search(what=role.name, country='gb', results=20)
        if not results:
            results = client.search(what=role.name, country='us', results=20)
        expires = timezone.now() + timedelta(hours=48)
        for raw in results:
            data = client.normalize_job(raw)
            if not data['adzuna_id']:
                continue
            JobListing.objects.update_or_create(
                adzuna_id=data['adzuna_id'],
                defaults={**data, 'matched_role': role, 'expires_at': expires}
            )
    except Exception as e:
        logger.warning(f'Adzuna refresh skipped: {e}')


@login_required
def job_board(request):
    from apps.core.models import UserActivity
    query = request.GET.get('q', '').strip()
    location_filter = request.GET.get('location', '').strip()

    # Get user skills
    user_skills = set()
    try:
        skills_qs = request.user.resume.skills.values_list('name', flat=True)
        user_skills = {s.lower().strip() for s in skills_qs}
    except Exception:
        pass

    jobs_qs = JobListing.objects.filter(expires_at__gt=timezone.now())
    if query:
        from django.db.models import Q
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query) | Q(company__icontains=query) | Q(description__icontains=query)
        )
    if location_filter:
        jobs_qs = jobs_qs.filter(location__icontains=location_filter)

    jobs_list = list(jobs_qs.select_related('matched_role')[:200])

    for job in jobs_list:
        # skill_tags is a JSONField (list)
        job_tags = {t.lower().strip() for t in (job.skill_tags or [])} - {''}
        matched = user_skills & job_tags
        missing = job_tags - user_skills
        job.match_score = round(len(matched) / max(len(job_tags), 1) * 100) if job_tags else 0
        job.matched_skills = sorted(matched)[:6]
        job.missing_skills = sorted(missing)[:4]

    jobs_list.sort(key=lambda j: (j.match_score, j.salary_max or 0), reverse=True)

    # Log activity
    if query or location_filter:
        try:
            UserActivity.objects.create(
                user=request.user,
                action='job_search',
                detail=f"q={query} loc={location_filter}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass

    locations = (
        JobListing.objects
        .filter(expires_at__gt=timezone.now())
        .values_list('location', flat=True)
        .distinct()[:30]
    )

    return render(request, 'jobs/board.html', {
        'jobs': jobs_list,
        'query': query,
        'location_filter': location_filter,
        'locations': [loc for loc in locations if loc],
        'has_resume': bool(user_skills),
        'user_skills': user_skills,
    })


@login_required
def job_detail(request, pk):
    from apps.core.models import UserActivity
    job = get_object_or_404(JobListing, pk=pk, expires_at__gt=timezone.now())

    user_skills = set()
    try:
        skills_qs = request.user.resume.skills.values_list('name', flat=True)
        user_skills = {s.lower().strip() for s in skills_qs}
    except Exception:
        pass

    job_tags = {t.lower().strip() for t in (job.skill_tags or [])} - {''}
    matched = user_skills & job_tags
    missing = job_tags - user_skills
    job.match_score = round(len(matched) / max(len(job_tags), 1) * 100) if job_tags else 0
    job.matched_skills = sorted(matched)
    job.missing_skills = sorted(missing)

    similar = JobListing.objects.filter(
        matched_role=job.matched_role,
        expires_at__gt=timezone.now()
    ).exclude(pk=pk).select_related('matched_role')[:6]

    try:
        UserActivity.objects.create(
            user=request.user, action='job_view',
            detail=f"{job.title} at {job.company}",
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    except Exception:
        pass

    return render(request, 'jobs/detail.html', {
        'job': job,
        'similar': similar,
    })


@login_required
def job_search_api(request):
    """AJAX search endpoint."""
    q = request.GET.get('q', '').strip()
    role_id = request.GET.get('role_id')

    jobs = JobListing.objects.filter(expires_at__gt=timezone.now())
    if q:
        from django.db.models import Q
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(location__icontains=q))
    if role_id:
        jobs = jobs.filter(matched_role_id=role_id)

    data = [
        {
            'id': j.id,
            'title': j.title,
            'company': j.company,
            'location': j.location,
            'salary': j.salary_display,
            'url': j.redirect_url,
            'category': j.category,
            'skill_tags': j.skill_tags[:5],
        }
        for j in jobs[:30]
    ]
    return JsonResponse({'results': data, 'count': len(data)})
