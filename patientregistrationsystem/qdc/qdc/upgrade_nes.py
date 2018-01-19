# Script to upgrade NES version

import pip
from django.conf import settings
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

from git import Repo


def get_current_path():
    base_dir = settings.BASE_DIR.split('/')
    path_git_repo = []
    for item in base_dir:
        if item != 'nes' and item != '':
            path_git_repo.append(item)
        if item == 'nes':
            path_git_repo.append(item)
            break
    path_repo = '/'
    for item in path_git_repo:
        path_repo = path_repo + item + '/'

    return path_repo


def get_pending_migrations():

    connection = connections[DEFAULT_DB_ALIAS]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return executor.migration_plan(targets)


def upgrade_nes():
    path_git_repo_local = get_current_path()
    repo = Repo(path_git_repo_local)

    for remote in repo.remotes:
        remote.fetch()

    git = repo.git
    tags = sorted(repo.tags, key=lambda t:t.commit.committed_datetime)
    last_tag = str(tags[-1])
    repo_version = last_tag.split('-')[-1]
    git.checkout(last_tag)

    try:
        pip.main(['install', '-r', 'requirements.txt'])
    except SystemExit as e:
        pass

    call_command('collectstatic', interactive=False, verbosity=0)

    if get_pending_migrations():
        call_command('migrate')
        return True


