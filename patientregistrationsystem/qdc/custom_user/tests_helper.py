from django.contrib.auth.models import User
from faker import Factory


def create_user(groups, username=None, force_password_change=False):
    """
    Create user to login in NES
    :param groups: QuerySet with groups of permissions to add to the user
    :param username: username
    :param force_password_change: False avoids to enter in password change page
    :return:
    """
    faker = Factory.create()

    password = 'passwd'
    user = User.objects.create_user(
        username=username or faker.name(), password=password
    )
    user.user_profile.login_enabled = True
    # disable force_password_change to avoid this step by now
    user.user_profile.force_password_change = force_password_change
    user.user_profile.save()

    for group in groups:
        user.groups.add(group)

    return [user, password]
