from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from patient.models import COUNTRIES


LOGIN = (
    (False, _('No')),
    (True, _('Yes, a username and password must be configured')),
)


class Institution(models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=30, unique=True)
    country = models.CharField(max_length=30, choices=COUNTRIES)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['name']


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.CASCADE)
    login_enabled = models.BooleanField(default=False, choices=LOGIN)
    force_password_change = models.BooleanField(default=True)
    citation_name = models.CharField(max_length=150, blank=True, default="")


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
