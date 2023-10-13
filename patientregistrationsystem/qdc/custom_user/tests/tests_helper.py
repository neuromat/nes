from django.contrib.auth.models import Group, User
from faker import Factory, Generator


def create_user(
    groups=Group.objects.none(),
    username=None,
    force_password_change=False,
    superuser=False,
):
    """
    Create user to login in NES
    :param groups: QuerySet with groups of permissions to add to the user
    :param username: username
    :param force_password_change: False avoids to enter in password change page
    :return:
    """
    fake: Generator = Factory.create()

    password = "passwd"
    if username is None:
        while True:
            username = fake.profile()["username"]
            if not User.objects.filter(username=username):
                break
    if superuser:
        user: User = User.objects.create_superuser(
            username=username,
            password=password,
            email=fake.profile()["mail"],
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
    else:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=fake.profile()["mail"],
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
    user.user_profile.login_enabled = True
    # Disable force_password_change to avoid this step by now
    user.user_profile.force_password_change = force_password_change
    user.user_profile.save()

    for group in groups:
        user.groups.add(group)

    return [user, password]
