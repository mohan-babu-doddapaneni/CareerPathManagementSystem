from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import OccupationRole, RequiredSkill, SkillGapReport
from collections import defaultdict


def _get_user_skills(user):
    try:
        return set(s.name.lower() for s in user.resume.skills.all())
    except Exception:
        return set()


@login_required
def analyse_page(request):
    roles = OccupationRole.objects.all()
    reports = SkillGapReport.objects.filter(user=request.user).select_related('role')
    return render(request, 'skills/analyse.html', {'roles': roles, 'reports': reports})


@login_required
def gap_analysis(request):
    role_id = request.GET.get('role_id')
    if not role_id:
        return JsonResponse({'error': 'role_id required'}, status=400)

    try:
        role = OccupationRole.objects.get(pk=role_id)
    except OccupationRole.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)

    user_skills = _get_user_skills(request.user)

    req_skills = list(role.required_skills.filter(category='technical').values('name', 'importance'))
    req_certs = list(role.required_skills.filter(category='certification').values('name', 'importance'))
    req_advanced = list(role.required_skills.filter(category='advanced').values('name', 'importance'))

    matched = [s for s in req_skills if s['name'].lower() in user_skills]
    missing = [s for s in req_skills if s['name'].lower() not in user_skills]

    total = len(req_skills)
    pct = round((len(matched) / total) * 100, 1) if total else 0

    # Cache the result
    SkillGapReport.objects.update_or_create(
        user=request.user, role=role,
        defaults={
            'match_percentage': pct,
            'matched_skills': [s['name'] for s in matched],
            'missing_skills': [s['name'] for s in missing],
            'missing_certifications': [s['name'] for s in req_certs],
            'missing_advanced': [s['name'] for s in req_advanced],
        }
    )

    return JsonResponse({
        'role': role.name,
        'match_percentage': pct,
        'matched': [s['name'] for s in matched],
        'missing': [s['name'] for s in missing],
        'certifications': [s['name'] for s in req_certs],
        'advanced': [s['name'] for s in req_advanced],
    })


@login_required
def predict_role(request):
    user_skills = _get_user_skills(request.user)
    roles = OccupationRole.objects.prefetch_related('required_skills')
    scores = {}

    for role in roles:
        req = set(s.name.lower() for s in role.required_skills.filter(category='technical'))
        if not req:
            continue
        matches = len(user_skills & req)
        scores[role.name] = round((matches / len(req)) * 100, 1)

    scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    best = next(iter(scores), None)
    return render(request, 'skills/predict_role.html', {'scores': scores, 'best': best})
