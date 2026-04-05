from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Resume, ParsedSkill, ParsedEducation, ParsedExperience, ParsedCertification
from .parser import parse_resume

ALLOWED_EXTENSIONS = ('.pdf', '.docx', '.doc')


@login_required
def resume_page(request):
    try:
        resume = request.user.resume
    except Resume.DoesNotExist:
        resume = None
    return render(request, 'resumes/resume.html', {'resume': resume})


@login_required
def upload_resume(request):
    if request.method != 'POST':
        return redirect('core:resume')

    uploaded = request.FILES.get('file')
    if not uploaded:
        messages.error(request, 'No file selected.')
        return redirect('core:resume')

    ext = uploaded.name.lower().rsplit('.', 1)[-1]
    if f'.{ext}' not in ALLOWED_EXTENSIONS:
        messages.error(request, 'Only .pdf or .docx files are supported.')
        return redirect('core:resume')

    # Delete old resume
    try:
        request.user.resume.delete()
    except Resume.DoesNotExist:
        pass

    try:
        parsed = parse_resume(uploaded, filename=uploaded.name)
    except Exception as e:
        messages.error(request, f'Could not parse resume: {e}')
        return redirect('core:resume')

    uploaded.seek(0)

    resume = Resume.objects.create(
        user=request.user,
        file=uploaded,
        original_filename=uploaded.name,
        raw_text=parsed['raw_text'],
        summary=parsed.get('summary', ''),
        linkedin_url=parsed.get('linkedin', ''),
        github_url=parsed.get('github', ''),
        parsed_at=timezone.now(),
    )

    # Skills
    for name in parsed.get('skills', []):
        ParsedSkill.objects.get_or_create(resume=resume, name=name,
                                          defaults={'source': 'parsed'})

    # Education
    for edu in parsed.get('education', []):
        ParsedEducation.objects.create(
            resume=resume,
            degree=edu.get('degree', ''),
            institution=edu.get('institution', ''),
            year=edu.get('year', ''),
            source='parsed',
        )

    # Experience
    for exp in parsed.get('experience', []):
        ParsedExperience.objects.create(
            resume=resume,
            job_title=exp.get('title', ''),
            company=exp.get('company', ''),
            duration_text=exp.get('date_range', ''),
            years=exp.get('years', 0),
            source='parsed',
        )

    # Certifications
    for cert in parsed.get('certifications', []):
        ParsedCertification.objects.get_or_create(
            resume=resume,
            name=cert.get('name', ''),
            defaults={
                'issuer': cert.get('issuer', ''),
                'year': cert.get('year', ''),
                'source': 'parsed',
            },
        )

    skill_count = len(parsed.get('skills', []))
    cert_count = len(parsed.get('certifications', []))
    edu_count = len(parsed.get('education', []))
    exp_count = len(parsed.get('experience', []))

    messages.success(
        request,
        f"Resume parsed! Found {skill_count} skills, {edu_count} education entries, "
        f"{exp_count} experience entries, {cert_count} certifications."
    )

    # Auto-fill phone from resume if profile missing it
    if parsed.get('phone') and not request.user.profile.phone:
        request.user.profile.phone = parsed['phone']
        request.user.profile.save()

    return redirect('core:resume')


@login_required
def delete_resume(request):
    if request.method == 'POST':
        try:
            request.user.resume.delete()
            messages.success(request, 'Resume deleted.')
        except Resume.DoesNotExist:
            pass
    return redirect('core:resume')


# ─── SKILLS ───────────────────────────────────────────────────────────────────

@login_required
def add_skill(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            resume, _ = Resume.objects.get_or_create(
                user=request.user,
                defaults={'original_filename': 'manual', 'raw_text': ''},
            )
            ParsedSkill.objects.get_or_create(resume=resume, name=name,
                                              defaults={'source': 'manual'})
            messages.success(request, f'Skill "{name}" added.')
    return redirect('core:resume')


@login_required
def delete_skill(request, pk):
    if request.method == 'POST':
        skill = get_object_or_404(ParsedSkill, pk=pk, resume__user=request.user)
        skill.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
    return redirect('core:resume')


# ─── EDUCATION ────────────────────────────────────────────────────────────────

@login_required
def add_education(request):
    if request.method == 'POST':
        degree = request.POST.get('degree', '').strip()
        institution = request.POST.get('institution', '').strip()
        year = request.POST.get('year', '').strip()
        if degree:
            resume, _ = Resume.objects.get_or_create(
                user=request.user,
                defaults={'original_filename': 'manual', 'raw_text': ''},
            )
            ParsedEducation.objects.create(
                resume=resume, degree=degree,
                institution=institution, year=year, source='manual',
            )
            messages.success(request, 'Education added.')
    return redirect('core:resume')


@login_required
def delete_education(request, pk):
    if request.method == 'POST':
        edu = get_object_or_404(ParsedEducation, pk=pk, resume__user=request.user)
        edu.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
    return redirect('core:resume')


# ─── EXPERIENCE ───────────────────────────────────────────────────────────────

@login_required
def add_experience(request):
    if request.method == 'POST':
        resume, _ = Resume.objects.get_or_create(
            user=request.user,
            defaults={'original_filename': 'manual', 'raw_text': ''},
        )
        ParsedExperience.objects.create(
            resume=resume,
            job_title=request.POST.get('job_title', '').strip(),
            company=request.POST.get('company', '').strip(),
            duration_text=request.POST.get('duration_text', '').strip(),
            years=request.POST.get('years', 0) or 0,
            source='manual',
        )
        messages.success(request, 'Experience added.')
    return redirect('core:resume')


@login_required
def delete_experience(request, pk):
    if request.method == 'POST':
        exp = get_object_or_404(ParsedExperience, pk=pk, resume__user=request.user)
        exp.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
    return redirect('core:resume')


# ─── CERTIFICATIONS ───────────────────────────────────────────────────────────

@login_required
def add_certification(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        issuer = request.POST.get('issuer', '').strip()
        year = request.POST.get('year', '').strip()
        if name:
            resume, _ = Resume.objects.get_or_create(
                user=request.user,
                defaults={'original_filename': 'manual', 'raw_text': ''},
            )
            ParsedCertification.objects.get_or_create(
                resume=resume, name=name,
                defaults={'issuer': issuer, 'year': year, 'source': 'manual'},
            )
            messages.success(request, f'Certification "{name}" added.')
    return redirect('core:resume')


@login_required
def delete_certification(request, pk):
    if request.method == 'POST':
        cert = get_object_or_404(ParsedCertification, pk=pk, resume__user=request.user)
        cert.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
    return redirect('core:resume')
