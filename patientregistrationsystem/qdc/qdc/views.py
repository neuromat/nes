import os
import platform
import sys
from functools import partial
from pathlib import Path

import pip
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations import Migration
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import activate
from django.utils.translation import gettext as _
from git.repo import Repo
from packaging.version import Version


def qdc_permission_denied_view(
    request: HttpRequest, exception, template_name: str = "admin/qdc_403.html"
) -> HttpResponse:
    context = {"exception": exception}

    return render(request, template_name, context, status=403)


@login_required
def contact(request: HttpRequest) -> HttpResponse:
    # messages.success(request, _("Test !"))
    if_upgrade = False
    if check_upgrade(request):
        if_upgrade = True
        if request.user.has_perm("configuration.upgrade_rights"):
            messages.info(
                request,
                mark_safe(
                    '<a href="/home/upgrade_nes/">There is a new version of NES. Click '
                    "for upgrade</a>"
                ),
            )

        else:
            messages.success(
                request,
                _(
                    "There is a new version, please contact your NES administrator to update !"
                ),
            )

    context = {
        "logo_institution": settings.LOGO_INSTITUTION,
        "if_upgrade": if_upgrade,
    }

    return render(request, "base/contato.html", context)


@login_required
def language_change(request: HttpRequest, language_code: str) -> HttpResponseRedirect:
    activate(language_code)
    request.session["_language"] = language_code

    return HttpResponseRedirect(request.GET["next"])


@login_required
def password_changed(request: HttpRequest) -> HttpResponse:
    messages.success(request, _("Password changed successfully."))

    return contact(request)


def check_upgrade(request: HttpRequest) -> bool:
    path_git_repo_local = get_nes_directory_path()
    list_dir = os.listdir(path_git_repo_local)
    new_version = False
    if ".git" in list_dir:
        repo = Repo(path_git_repo_local)
        git = repo.git
        current_tag = git.description
        if current_tag in repo.tags:
            repo.remotes.origin.fetch()
            new_version_tag = sorted(
                git.tag().split("\n"),
                key=lambda s: list(map(int, s.replace("-", ".").split(".")[1:])),
            )[-1]
            new_version = Version(current_tag.split("-")[-1]) < Version(
                new_version_tag.split("-")[-1]
            )

    else:
        messages.success(
            request,
            _(
                "You dont have NES Git installation. Automatic upgrade can be done with git "
                "installation. "
                "Please contact your system administrator to upgrade NES to a new version."
            ),
        )

    return new_version


def get_nes_directory_path() -> str:
    path_repo = "/"
    if "Windows" in platform.system():
        path_repo = ""
    base_dir = str(settings.BASE_DIR).split("/")
    if "nes" in base_dir:
        path_git_repo = []
        for item in base_dir:
            if item != "nes" and item != "":
                path_git_repo.append(item)
            if item == "nes":
                path_git_repo.append(item)
                break

        for item in path_git_repo:
            path_repo = path_repo + item + "/"

    return path_repo


def get_pending_migrations() -> list[tuple[Migration, bool]]:
    connection = connections[DEFAULT_DB_ALIAS]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return executor.migration_plan(targets)


@login_required
@permission_required("configuration.upgrade_rights", raise_exception=True)
def upgrade_nes(request: HttpRequest) -> HttpResponseRedirect:
    path_git_repo_local = get_nes_directory_path()
    list_dir = os.listdir(path_git_repo_local)

    # criate a log file in path_git_repo_local + 'patientregistrationsystem'
    log_file = os.path.join(settings.BASE_DIR, "upgrade.log")
    log = open(log_file, "w", encoding="utf-8")
    sys.stdout = log

    if ".git" in list_dir:
        repo = Repo(path_git_repo_local)
        git = repo.git

        new_version_tag = sorted(
            git.tag().split("\n"),
            key=lambda s: list(map(int, s.replace("-", ".").split(".")[1:])),
        )[-1]

        repo.remotes.origin.fetch()

        git.checkout(new_version_tag)

        try:
            pip.main(["install", "-r", "requirements.txt"])
        except SystemExit:
            pass

        call_command("collectstatic", interactive=False, verbosity=0)

        if get_pending_migrations():
            call_command("migrate")
        else:
            print("There are not migrations")

        os.system(
            f"touch {path_git_repo_local}patientregistrationsystem/qdc/qdc/wsgi.py"
        )

        # check if the current TAG is the latest tag
        if git.describe() == new_version_tag:
            messages.success(request, _("Updated!!! Enjoy the new version of NES  :-)"))
            print("NES updated to " + new_version_tag)
        else:
            messages.info(
                request,
                _(
                    "An unknown error ocurred ! Please contact your administrator system."
                ),
            )
            print("NES was not updated " + new_version_tag)

    redirect_url = reverse("contact", args=())
    return HttpResponseRedirect(redirect_url)
