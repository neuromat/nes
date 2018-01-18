# check if exist a NES new version

from django.conf import settings
from git import Repo


def check_upgrade():
    repo = Repo("/Users/mruizo/PycharmProjects/nes/.git")
    for remote in repo.remotes:
        remote.fetch()

    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

    remote_version = str(tags[-1]).split('-')[-1]
    remote_version = remote_version.split('.')
    current_version = settings.VERSION.split('.')
    print(remote_version)
    print(current_version)
    if int(remote_version[0]) == int(current_version[0]):
        if int(remote_version[1]) > int(current_version[1]):
            return True
        else:
            if int(remote_version[1]) == int(current_version[1]):
                if int(remote_version[2]) > int(current_version[2]):
                    return True
                else:
                    if int(remote_version[2]) == int(current_version[2]):
                        return False
    else:
        if int(remote_version[0]) > int(current_version[0]):
            return True
        else:
            return False
