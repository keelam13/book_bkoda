from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create or update a UserProfile instance whenever a User is created or saved.
    - If 'created' is True (new user), a new UserProfile is created.
    - If 'created' is False (existing user saved), the associated UserProfile is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
