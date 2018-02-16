from django.contrib.auth.models import User, Group

TEST_PASSWORD = 'suzana@nes'


def create_user(group_name, username=None):
    if not username:
        username = 'suzana'
    user = User.objects.create_user(
        username=username, password=TEST_PASSWORD
    )
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()
    return user
