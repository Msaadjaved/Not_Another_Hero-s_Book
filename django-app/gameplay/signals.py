from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created, or save existing profile"""
    if created:
        # Only create if user is new AND doesn't have a profile
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance, role='reader')
    else:
        # User already exists, just save the profile if it exists
        if hasattr(instance, 'profile'):
            instance.profile.save()