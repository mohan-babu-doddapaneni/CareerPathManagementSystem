from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
from allauth.account.signals import user_logged_in, user_logged_out


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


@receiver(user_logged_in)
def log_login(request, user, **kwargs):
    try:
        from apps.core.models import UserActivity
        UserActivity.objects.create(
            user=user,
            action='login',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_logout(request, user, **kwargs):
    try:
        if user:
            from apps.core.models import UserActivity
            UserActivity.objects.create(
                user=user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
    except Exception:
        pass
