import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import activate, LANGUAGE_SESSION_KEY, ugettext as _
from git import Repo
import pip
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor


def qdc_permission_denied_view(request, template_name="admin/qdc_403.html"):

    context = {}

    return render(request, template_name, context, status=403)


@login_required
def contact(request):
    context = {
        'logo_institution': settings.LOGO_INSTITUTION,
    }
    if check_upgrade(request):
        messages.success(request, _("There is a new version, please contact your administrator to update !"))
    else:
        messages.success(request, _("There is not a new version !"))


    return render(request, 'quiz/contato.html', context)


@login_required
def language_change(request, language_code):

    activate(language_code)
    request.session[LANGUAGE_SESSION_KEY] = language_code

    return HttpResponseRedirect(request.GET['next'])


@login_required
def password_changed(request):

    messages.success(request, _('Password changed successfully.'))

    return contact(request)


@login_required
def check_upgrade(request):
    repo = Repo("/Users/mruizo/PycharmProjects/nes/.git")
    for remote in repo.remotes:
        remote.fetch()

    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

    remote_version = str(tags[-1]).split('-')[-1]
    remote_version = remote_version.split('.')
    local_current_version = settings.VERSION.split('.')
    print(remote_version)
    print(local_current_version)
    if int(remote_version[0]) == int(local_current_version[0]):
        if int(remote_version[1]) > int(local_current_version[1]):
            # messages.success(request, _("There is a new version to upgrade!"))
            return True
        else:
            if int(remote_version[1]) == int(local_current_version[1]):
                if int(remote_version[2]) == int(local_current_version[2]):
                    # messages.success(request, _("There is a new version to upgrade!"))
                    return False
                else:
                    return True
    else:
        if int(remote_version[0]) > int(local_current_version[0]):
            # messages.success(request, _("There is a new version to upgrade!"))
            return True
        else:
            # messages.success(request, _("There is not a new version to upgrade!"))
            return False
    # return render(request, "quiz/contato.html")


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


@login_required
def upgrade_nes(request):
    log = open("upgrade.log", "a")
    sys.stdout = log
    path_git_repo_local = get_current_path()
    repo = Repo(path_git_repo_local)

    for remote in repo.remotes:
        remote.fetch()

    git = repo.git
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    last_tag = str(tags[-2]) # last version [-1] before last version [-2]
    repo_version = last_tag.split('-')[-2]
    print("repository last version: " + repo_version)
    git.checkout(last_tag)

    try:
        pip.main(['install', '-r', 'requirements.txt'])
    except SystemExit as e:
        pass

    call_command('collectstatic', interactive=False, verbosity=0)

    if get_pending_migrations():
        call_command('migrate')

    messages.success(request, _("Upgrade to version " + repo_version + " was sucessful!"))

    return render(request, 'quiz/contato.html')
