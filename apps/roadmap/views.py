from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from apps.skills.models import OccupationRole, RequiredSkill
from apps.core.models import UserActivity
from .models import CareerGoal, LearningStep


def _get_user_skills(user):
    try:
        return {s.name.lower() for s in user.resume.skills.all()}
    except Exception:
        return set()


@login_required
def set_goal(request):
    roles = cache.get('occupation_roles_list')
    if not roles:
        roles = list(OccupationRole.objects.all())
        cache.set('occupation_roles_list', roles, 3600)

    existing = getattr(request.user, 'career_goal', None)

    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        target_date = request.POST.get('target_date') or None
        if not role_id:
            messages.error(request, 'Please select a target role.')
            return render(request, 'roadmap/set_goal.html', {'roles': roles, 'existing': existing})

        role = get_object_or_404(OccupationRole, pk=role_id)
        goal, _ = CareerGoal.objects.update_or_create(
            user=request.user,
            defaults={'target_role': role, 'target_date': target_date, 'status': 'active'},
        )

        # Rebuild steps from skill gap
        goal.steps.all().delete()
        user_skills = _get_user_skills(request.user)
        req_skills = RequiredSkill.objects.filter(role=role).order_by('category', '-importance')

        steps = []
        for i, rs in enumerate(req_skills):
            if rs.name.lower() not in user_skills:
                steps.append(LearningStep(
                    goal=goal,
                    skill_name=rs.name,
                    category=rs.category,
                    order=i,
                ))
        LearningStep.objects.bulk_create(steps)

        UserActivity.objects.create(
            user=request.user, action='skill_add',
            detail=f"Set career goal: {role.name}",
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        messages.success(request, f'Career goal set! Your roadmap to {role.name} is ready.')
        return redirect('core:roadmap')

    return render(request, 'roadmap/set_goal.html', {'roles': roles, 'existing': existing})


@login_required
def roadmap(request):
    try:
        goal = (CareerGoal.objects
                .select_related('target_role')
                .prefetch_related('steps')
                .get(user=request.user, status='active'))
    except CareerGoal.DoesNotExist:
        return redirect('core:set_goal')

    steps_by_category = {}
    for step in goal.steps.all():
        steps_by_category.setdefault(step.category, []).append(step)

    completion = goal.completion_pct()
    return render(request, 'roadmap/roadmap.html', {
        'goal': goal,
        'steps_by_category': steps_by_category,
        'completion': completion,
    })


@login_required
def update_step(request, pk):
    step = get_object_or_404(LearningStep, pk=pk, goal__user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ('pending', 'learning', 'done'):
            step.status = new_status
            step.save(update_fields=['status', 'updated_at'])
    return redirect('core:roadmap')
