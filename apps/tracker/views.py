from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.core.models import UserActivity
from .models import JobApplication


KANBAN_COLUMNS = [
    ('saved', 'Saved', '🔖'),
    ('applied', 'Applied', '📤'),
    ('phone_screen', 'Phone Screen', '📞'),
    ('interview', 'Interview', '🎤'),
    ('offer', 'Offer', '🎉'),
    ('rejected', 'Rejected', '❌'),
]


@login_required
def tracker_board(request):
    apps = JobApplication.objects.filter(user=request.user)
    columns = []
    for status, label, icon in KANBAN_COLUMNS:
        columns.append({
            'status': status,
            'label': label,
            'icon': icon,
            'items': [a for a in apps if a.status == status],
        })

    stats = {
        'total': apps.count(),
        'applied': apps.filter(status='applied').count(),
        'interviews': apps.filter(status='interview').count(),
        'offers': apps.filter(status='offer').count(),
    }

    return render(request, 'tracker/board.html', {
        'columns': columns,
        'stats': stats,
    })


@login_required
def add_application(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_listing_id')
        job_listing = None
        if job_id:
            from apps.jobs.models import JobListing
            try:
                job_listing = JobListing.objects.get(pk=job_id)
            except JobListing.DoesNotExist:
                pass

        app = JobApplication.objects.create(
            user=request.user,
            job_title=request.POST.get('job_title', ''),
            company=request.POST.get('company', ''),
            location=request.POST.get('location', ''),
            job_url=request.POST.get('job_url', ''),
            status=request.POST.get('status', 'saved'),
            notes=request.POST.get('notes', ''),
            applied_date=request.POST.get('applied_date') or None,
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            contact_name=request.POST.get('contact_name', ''),
            contact_email=request.POST.get('contact_email', ''),
            job_listing=job_listing,
        )
        try:
            UserActivity.objects.create(
                user=request.user, action='job_view',
                detail=f"Tracked: {app.job_title} @ {app.company}",
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass
        messages.success(request, f'Added "{app.job_title}" to your tracker.')
        next_url = request.POST.get('next', '')
        return redirect(next_url or 'core:tracker')
    return redirect('core:tracker')


@login_required
def update_application(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        app.status = request.POST.get('status', app.status)
        app.notes = request.POST.get('notes', app.notes)
        app.contact_name = request.POST.get('contact_name', app.contact_name)
        app.contact_email = request.POST.get('contact_email', app.contact_email)
        app.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'status': app.get_status_display()})
    return redirect('core:tracker')


@login_required
def delete_application(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        app.delete()
        messages.success(request, 'Application removed.')
    return redirect('core:tracker')
