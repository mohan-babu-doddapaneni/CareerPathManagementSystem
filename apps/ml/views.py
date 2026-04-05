from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import TrainedModel, ModelPerformance, JobDataset
from .classifier import predict, train_model, ALGORITHM_MAP


@login_required
def ml_dashboard(request):
    performances = ModelPerformance.objects.select_related('model').order_by('-model__trained_at')
    algorithms = list(ALGORITHM_MAP.keys())
    return render(request, 'ml/dashboard.html', {
        'performances': performances,
        'algorithms': algorithms,
    })


@login_required
def prediction_form(request):
    user = request.user
    skills_str = ''
    education = ''
    experience = 0

    try:
        resume = user.resume
        skills_str = ', '.join(s.name for s in resume.skills.all())
        edu_list = list(resume.education.values_list('degree', flat=True))
        education = ', '.join(edu_list) if edu_list else 'Bachelor'
        exp_qs = resume.experiences.all()
        if exp_qs.exists():
            experience = int(exp_qs.first().years)
    except Exception:
        pass

    if request.method == 'POST':
        skills_str = request.POST.get('skills', skills_str)
        experience = request.POST.get('experience', experience)
        education = request.POST.get('education', education)
        algorithm = request.POST.get('algorithm', 'random_forest')

        try:
            predicted_title = predict(skills_str, experience, education, algorithm)
            # Find jobs matching the predicted title
            matching = JobDataset.objects.filter(predicted_job_title=predicted_title)
            predicted = matching.first()
            relevant = matching[1:10] if matching.count() > 1 else JobDataset.objects.none()
            return render(request, 'ml/results.html', {
                'predicted': predicted,
                'predicted_title': predicted_title,
                'relevant': relevant,
                'skills': skills_str,
                'experience': experience,
                'education': education,
            })
        except ValueError as e:
            messages.error(request, str(e))

    algorithms = list(ALGORITHM_MAP.keys())
    return render(request, 'ml/predict.html', {
        'skills': skills_str,
        'education': education,
        'experience': experience,
        'algorithms': algorithms,
    })


@staff_member_required
def train_model_view(request, algorithm):
    if algorithm not in ALGORITHM_MAP:
        messages.error(request, f'Unknown algorithm: {algorithm}')
        return redirect('core:ml_dashboard')

    try:
        _, metrics = train_model(algorithm)
        messages.success(
            request,
            f'{algorithm.replace("_", " ").title()} trained — '
            f'Accuracy: {metrics["accuracy"]*100:.1f}%'
        )
    except Exception as e:
        messages.error(request, f'Training failed: {e}')

    return redirect('core:ml_dashboard')
