from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'core/home.html')


def health(request):
    return JsonResponse({'status': 'ok'})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        from django.shortcuts import redirect
        return redirect('core:dashboard')

    from apps.resumes.models import Resume, ParsedSkill
    from apps.core.models import UserActivity
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    from django.utils import timezone
    import datetime

    User = get_user_model()

    now = timezone.now()
    week_ago = now - datetime.timedelta(days=7)

    total_users = User.objects.filter(is_active=True).count()
    total_resumes = Resume.objects.count()
    recent_signups = User.objects.filter(date_joined__gte=week_ago).count()
    total_activities = UserActivity.objects.count()

    top_skills = (ParsedSkill.objects.values('name')
                  .annotate(count=Count('id'))
                  .order_by('-count')[:10])

    # Recent activity
    recent_activity = UserActivity.objects.select_related('user').order_by('-created_at')[:20]

    # Activity breakdown
    action_counts = (UserActivity.objects.values('action')
                     .annotate(count=Count('id'))
                     .order_by('-count'))

    # Recent signups
    recent_users = User.objects.order_by('-date_joined')[:10]

    # Daily activity for chart (last 7 days)
    daily_activity = []
    for i in range(6, -1, -1):
        day = now - datetime.timedelta(days=i)
        count = UserActivity.objects.filter(
            created_at__date=day.date()
        ).count()
        daily_activity.append({'date': day.strftime('%b %d'), 'count': count})

    return render(request, 'core/admin_dashboard.html', {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'recent_signups': recent_signups,
        'total_activities': total_activities,
        'top_skills': top_skills,
        'recent_activity': recent_activity,
        'action_counts': action_counts,
        'recent_users': recent_users,
        'daily_activity': daily_activity,
    })


@login_required
def dashboard(request):
    from apps.skills.models import SkillGapReport, OccupationRole
    from apps.jobs.models import JobListing
    from django.utils import timezone

    user = request.user
    profile = user.profile
    gap_reports = SkillGapReport.objects.filter(user=user).select_related('role')[:3]
    roles = OccupationRole.objects.all()

    # Skill/resume stats
    skill_count = 0
    experience_count = 0
    education_count = 0
    has_resume = False
    user_skills = set()
    try:
        resume = user.resume
        has_resume = bool(resume.file or resume.raw_text)
        skill_count = resume.skills.count()
        experience_count = resume.experiences.count()
        education_count = resume.education.count()
        user_skills = {s.lower().strip() for s in resume.skills.values_list('name', flat=True)}
    except Exception:
        pass

    # Top matching jobs (top 3)
    top_jobs = []
    try:
        jobs_qs = list(JobListing.objects.filter(expires_at__gt=timezone.now()).select_related('matched_role')[:100])
        for job in jobs_qs:
            job_tags = {t.lower().strip() for t in (job.skill_tags or [])} - {''}
            matched = user_skills & job_tags
            job.match_score = round(len(matched) / max(len(job_tags), 1) * 100) if job_tags else 0
            job.matched_skills = sorted(matched)[:3]
        jobs_qs.sort(key=lambda j: (j.match_score, j.salary_max or 0), reverse=True)
        top_jobs = jobs_qs[:3]
    except Exception:
        pass

    job_count = JobListing.objects.filter(expires_at__gt=timezone.now()).count()

    # Recent activity count
    recent_activity_count = 0
    try:
        from apps.core.models import UserActivity
        from django.utils import timezone as tz
        import datetime
        week_ago = tz.now() - datetime.timedelta(days=7)
        recent_activity_count = UserActivity.objects.filter(user=user, created_at__gte=week_ago).count()
    except Exception:
        pass

    context = {
        'profile': profile,
        'gap_reports': gap_reports,
        'roles': roles,
        'job_count': job_count,
        'skill_count': skill_count,
        'experience_count': experience_count,
        'education_count': education_count,
        'has_resume': has_resume,
        'top_jobs': top_jobs,
        'user_skills': user_skills,
        'recent_activity_count': recent_activity_count,
    }
    return render(request, 'core/dashboard.html', context)
