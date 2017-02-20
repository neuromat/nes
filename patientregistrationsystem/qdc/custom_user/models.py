from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # This is almost the same as
    # user = models.ForeignKey(User, unique=True)
    # See: http://stackoverflow.com/questions/5870537/whats-the-difference-between-django-onetoonefield-and-foreignkey
    user = models.OneToOneField(User, related_name='user_profile')
    force_password_change = models.BooleanField(default=True)


def create_user_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


def password_change_signal(sender, instance, **kwargs):
    try:

        if User.objects.all().count() == 0:
            return

        user = User.objects.get(username=instance.username)

        if user.is_superuser:
            return

        if not user.password == instance.password:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.force_password_change = False
            profile.save()
    except User.DoesNotExist:
        pass


signals.pre_save.connect(password_change_signal, sender=User, dispatch_uid='accounts.models')

signals.post_save.connect(create_user_profile_signal, sender=User, dispatch_uid='accounts.models')
