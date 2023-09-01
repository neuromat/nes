# check if exist a NES new version

import os

from django.conf import settings
from git.repo import Repo


def check_upgrade() -> bool:
    # FIXME arrumar isso
    print(os.path.dirname(os.path.abspath(__file__)))
    repo = Repo("https://github.com/mcostat/nes.git")
    for remote in repo.remotes:
        remote.fetch()

    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

    remote_version = str(tags[-1]).rsplit("-", 1)[-1]
    remote_version = remote_version.split(".")
    current_version = settings.VERSION.split(".")
    print(remote_version)
    print(current_version)
    if int(remote_version[0]) == int(current_version[0]):
        if int(remote_version[1]) > int(current_version[1]):
            return True
        elif int(remote_version[1]) == int(current_version[1]):
            if int(remote_version[2]) > int(current_version[2]):
                return True
            else:
                return False
        else:
            return False
    else:
        if int(remote_version[0]) > int(current_version[0]):
            return True
        else:
            return False
