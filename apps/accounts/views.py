from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from apps.skills.models import OccupationRole


@login_required
def profile(request):
    profile = request.user.profile
    roles = OccupationRole.objects.all()
    try:
        resume = request.user.resume
    except Exception:
        resume = None
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'roles': roles,
        'resume': resume,
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.save()

        profile = user.profile
        profile.phone = request.POST.get('phone', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        role_id = request.POST.get('target_role')
        if role_id:
            try:
                profile.target_role = OccupationRole.objects.get(pk=role_id)
            except OccupationRole.DoesNotExist:
                pass
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:profile')
    return redirect('core:profile')
