# your_app_name/utils.py
from django.contrib.auth.models import User
from image_app.models import Profile

def link_profiles_to_users():
    """
    This script links existing profiles to users with matching usernames.
    Run this once after updating models and applying migrations.
    """
    orphan_profiles = Profile.objects.filter(user__isnull=True)

    for profile in orphan_profiles:
        try:
            user = User.objects.get(username=profile.username)
            profile.user = user
            profile.save()
            print(f"Linked profile for {profile.username} to user.")
        except User.DoesNotExist:
            print(f"No user found for profile {profile.username}")

    print(f"Linked profiles: {Profile.objects.filter(user__isnull=False).count()}")
    print(f"Unlinked profiles: {Profile.objects.filter(user__isnull=True).count()}")
