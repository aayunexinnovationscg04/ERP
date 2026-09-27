"""Revoke a user's sessions whenever a security-relevant field changes."""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User

# A change to any of these invalidates every token the user holds.
_SENSITIVE = ("password", "is_active", "role", "company_id")


@receiver(pre_save, sender=User)
def bump_session_version(sender, instance, raw=False, **kwargs):
    if raw or not instance.pk:
        return
    old = User.objects.filter(pk=instance.pk).values(*_SENSITIVE).first()
    if old and any(old[f] != getattr(instance, f) for f in _SENSITIVE):
        instance.session_version += 1
