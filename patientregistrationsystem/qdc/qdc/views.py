import os
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
    path_git_repo_local = get_nes_directory_path()
    list_dir = os.listdir(path_git_repo_local)
    new_version = False
    if '.git' in list_dir:
        repo = Repo(path_git_repo_local)
        current_branch = repo.active_branch.name
        for remote in repo.remotes:
            remote.fetch()

        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        if tags:
            new_version = nes_new_version(tags)
            if new_version and 'TAG' not in current_branch.split('-'):
                messages.success(request, _("Not is possible automatically upgrade NES in your installation"
                                            " (Branch name " + current_branch + " ). Please contact your "
                                            "system administrator to upgrade NES to a new version."))

    else:
        messages.success(request, _("No NES Git installation. Automatic upgrade can be done with git installation. "
                                    "Please contact your system administrator to upgrade NES to a new version."))

    return new_version


def nes_new_version(tags):
    new_version = False
    remote_version = str(tags[-1]).split('-')[-1]
    remote_version = remote_version.split('.')
    local_current_version = settings.VERSION.split('.')
    print(remote_version)
    print(local_current_version)
    if int(remote_version[0]) > int(local_current_version[0]):
        new_version = True
    elif int(remote_version[0]) == int(local_current_version[0]):
        if int(remote_version[1]) > int(local_current_version[1]):
            new_version = True
        elif int(remote_version[1]) == int(local_current_version[1]):
            if int(remote_version[2]) > int(local_current_version[2]):
                new_version = True
    return new_version


def get_nes_directory_path():
    path_repo = '/'
    base_dir = settings.BASE_DIR.split('/')
    if 'nes' in base_dir:
        path_git_repo = []
        for item in base_dir:
            if item != 'nes' and item != '':
                path_git_repo.append(item)
            if item == 'nes':
                path_git_repo.append(item)
                break

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

    path_git_repo_local = get_nes_directory_path()
    list_dir = os.listdir(path_git_repo_local)
    if '.git' in list_dir:
        repo = Repo(path_git_repo_local)
        branch = repo.active_branch
        # if 'TAG' in branch.name.split('-'):
        for remote in repo.remotes:
            remote.fetch()

        git = repo.git
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        if tags:
            # if nes_new_version(tags):
            last_tag = str(tags[-1])  # last version [-1] before last version [-2]
            repo_version = last_tag.split('-')[-1]
            print("repository last version: " + repo_version)
            git.checkout(last_tag)

            try:
                pip.main(['install', '-r', 'requirements.txt'])
            except SystemExit as e:
                pass

            call_command('collectstatic', interactive=False, verbosity=0)

            if get_pending_migrations():
                call_command('migrate')

            # TODO start apache (opcao colocar um flag no setting local)
            # check the current branch - a tag mais nova last_tag
            if repo.active_branch.name == last_tag:
                messages.success(request, _("Upgrade to version " + repo_version + " was sucessful!"))
            else:
                messages.success(request, _("An error ocurred when upgrade to the new version ! Please contact "
                                            "your administrator system."))
        # else:
        #     messages.success(request, _("NES git branch different: " + branch.name + ". Please contact your system "
        #                                 "administrator to upgrade NES to the new version."))

    return render(request, 'quiz/contato.html')
