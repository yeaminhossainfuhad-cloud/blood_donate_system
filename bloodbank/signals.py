"""
Safety-net signal: if a User somehow exists without a DonorProfile
(e.g. a superuser created via createsuperuser), create a minimal one
the first time it's needed, instead of the site crashing on
`request.user.donor_profile`.
"""
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DonorProfile


@receiver(post_save, sender=User)
def ensure_donor_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'donor_profile'):
        DonorProfile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
                'blood_group': 'O+',
                'phone': '0000000000',
                'location': 'Unknown',
                'is_available': False,
            },
        )
