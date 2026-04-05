import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.cache import cache
from django.urls import reverse

from apps.resumes.models import Resume, ParsedSkill
from apps.core.models import UserActivity
from apps.skills.models import SkillGapReport, OccupationRole
from apps.jobs.models import JobListing
from apps.roadmap.models import CareerGoal, LearningStep
from apps.courses.models import Course
from apps.tracker.models import JobApplication


def home(request):
    return render(request, 'core/home.html')


def health(request):
    return JsonResponse({'status': 'ok'})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('core:dashboard')

    cache_key = 'admin_dashboard_stats'
    cached = cache.get(cache_key)
    if cached:
        return render(request, 'core/admin_dashboard.html', cached)

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

    # Daily activity for chart (last 7 days) — single aggregation query
    daily_qs = (UserActivity.objects
                .filter(created_at__date__gte=(now - datetime.timedelta(days=7)).date())
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(count=Count('id')))
    daily_map = {row['day']: row['count'] for row in daily_qs}
    daily_activity = [
        {'date': (now - datetime.timedelta(days=i)).strftime('%b %d'),
         'count': daily_map.get((now - datetime.timedelta(days=i)).date(), 0)}
        for i in range(6, -1, -1)
    ]

    ctx = {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'recent_signups': recent_signups,
        'total_activities': total_activities,
        'top_skills': list(top_skills),
        'recent_activity': list(recent_activity),
        'action_counts': list(action_counts),
        'recent_users': list(recent_users),
        'daily_activity': daily_activity,
    }
    cache.set(cache_key, ctx, 300)  # cache 5 min
    return render(request, 'core/admin_dashboard.html', ctx)


@login_required
def dashboard(request):
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

    # Career Goal / Roadmap
    goal = None
    goal_completion = 0
    pending_steps = []
    try:
        goal = CareerGoal.objects.select_related('target_role').get(user=user, status='active')
        goal_completion = goal.completion_pct()
        pending_steps = list(goal.steps.filter(status__in=['pending', 'learning'])[:5])
    except CareerGoal.DoesNotExist:
        pass

    # Top 3 course recommendations from skill gap
    top_courses = []
    if pending_steps:
        missing = {s.skill_name.lower() for s in pending_steps}
        all_courses = cache.get('all_courses_list') or list(Course.objects.all())
        matched = []
        for c in all_courses:
            tags = c.skill_list()
            hits = [t for t in tags if t in missing]
            if hits:
                c.match_count = len(hits)
                matched.append(c)
        matched.sort(key=lambda c: (-c.match_count, -(c.rating or 0)))
        top_courses = matched[:3]

    # Tracker stats
    tracker_stats = {'total': 0, 'interviews': 0, 'offers': 0}
    try:
        apps_qs = JobApplication.objects.filter(user=user)
        tracker_stats = {
            'total': apps_qs.count(),
            'interviews': apps_qs.filter(status='interview').count(),
            'offers': apps_qs.filter(status='offer').count(),
        }
    except Exception:
        pass

    quick_actions = [
        {'icon': '📄', 'label': 'My Resume', 'url': reverse('core:resume')},
        {'icon': '💼', 'label': 'Job Board', 'url': reverse('core:jobs')},
        {'icon': '📋', 'label': 'Tracker', 'url': reverse('core:tracker')},
        {'icon': '🗺️', 'label': 'Roadmap', 'url': reverse('core:roadmap')},
        {'icon': '📚', 'label': 'Courses', 'url': reverse('core:courses')},
        {'icon': '🤖', 'label': 'Career AI', 'url': reverse('core:prediction_form')},
    ]

    context = {
        'profile': profile,
        'gap_reports': gap_reports,
        'roles': roles,
        'job_count': job_count,
        'skill_count': skill_count,
        'exp_count': experience_count,
        'edu_count': education_count,
        'experience_count': experience_count,
        'education_count': education_count,
        'has_resume': has_resume,
        'top_jobs': top_jobs,
        'user_skills': user_skills,
        'goal': goal,
        'goal_completion': goal_completion,
        'pending_steps': pending_steps,
        'top_courses': top_courses,
        'quick_actions': quick_actions,
        'tracker_stats': tracker_stats,
    }
    return render(request, 'core/dashboard.html', context)
