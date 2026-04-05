from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import Course


def _get_user_skills(user):
    try:
        return {s.name.lower() for s in user.resume.skills.all()}
    except Exception:
        return set()


@login_required
def recommended_courses(request):
    """Show courses that match the user's skill gaps."""
    from apps.skills.models import OccupationRole
    from apps.roadmap.models import CareerGoal

    user_skills = _get_user_skills(request.user)

    # Try to get missing skills from active career goal first
    missing_skills = set()
    try:
        goal = CareerGoal.objects.select_related('target_role').get(
            user=request.user, status='active'
        )
        missing_skills = {
            s.skill_name.lower()
            for s in goal.steps.filter(status__in=['pending', 'learning'])
        }
    except CareerGoal.DoesNotExist:
        pass

    # Fall back to all skills from OccupationRole matching
    if not missing_skills and user_skills:
        from apps.skills.models import RequiredSkill
        all_req = RequiredSkill.objects.filter(
            category='technical'
        ).values_list('name', flat=True)
        missing_skills = {s.lower() for s in all_req} - user_skills

    # Find courses that cover missing skills (limit 12)
    all_courses = cache.get('all_courses_list')
    if all_courses is None:
        all_courses = list(Course.objects.all())
        cache.set('all_courses_list', all_courses, 3600)

    recommended = []
    for course in all_courses:
        tags = course.skill_list()
        matched = [t for t in tags if t in missing_skills]
        if matched:
            course.matched_skills = matched
            course.match_count = len(matched)
            recommended.append(course)

    recommended.sort(key=lambda c: (-c.match_count, -(c.rating or 0)))
    recommended = recommended[:12]

    filter_platform = request.GET.get('platform', '')
    filter_free = request.GET.get('free', '')
    if filter_platform:
        recommended = [c for c in recommended if c.platform == filter_platform]
    if filter_free == '1':
        recommended = [c for c in recommended if c.is_free]

    platforms = Course.objects.values_list('platform', flat=True).distinct()

    return render(request, 'courses/recommendations.html', {
        'courses': recommended,
        'missing_skills': sorted(missing_skills)[:15],
        'filter_platform': filter_platform,
        'filter_free': filter_free,
        'platforms': platforms,
    })
