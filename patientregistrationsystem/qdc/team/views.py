# coding=utf-8

import json

from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _

from .forms import PersonRegisterForm, TeamRegisterForm, TeamPersonRegisterForm, UserPersonForm
from .models import Person, Team, TeamPerson


@login_required
@permission_required('team.change_team')
def registers(request, template_name="team/registers.html"):
    register_list = [
        {
            'item': _('Persons'),
            'href': reverse("person_list", args=()),
            'quantity': Person.objects.all().count()
        },
        {
            'item': _('Teams'),
            'href': reverse("team_list", args=()),
            'quantity': Team.objects.all().count()
        },
    ]

    return render(request, template_name, context={"register_list": register_list})


@login_required
@permission_required('team.change_team')
def person_list(request, template_name='team/person_list.html'):
    return render(request, template_name, context={"persons": Person.objects.all().order_by('first_name')})


@login_required
@permission_required('team.change_team')
def person_create(request, template_name="team/person_register.html"):

    person_form = PersonRegisterForm(request.POST or None)
    user_form = UserPersonForm(request.POST or None)

    group_permissions = []
    groups = Group.objects.all()

    for group in groups:
        group_permissions.append(
            {'group': group,
             'checked': False}
        )

    if request.method == "POST":

        if request.POST['action'] == "save":

            if person_form.is_valid():

                new_user = None
                error_creating_user = False

                if request.POST['optradio'] == '2':
                    if user_form.is_valid():

                        if not User.objects.filter(email=request.POST['email']).exists():

                            new_user = user_form.save()
                            new_user.email = request.POST['email']
                            new_user.first_name = request.POST['first_name']
                            new_user.last_name = request.POST['last_name']
                            new_user.save()
                        else:
                            messages.warning(request, _('E-mail already exists.'))
                            error_creating_user = True
                    else:
                        messages.warning(request, _('Information not saved.'))
                        error_creating_user = True

                if not error_creating_user:

                    person_added = person_form.save(commit=False)
                    if new_user:
                        person_added.user = new_user
                    person_added.save()

                    # sync user
                    if person_added.user:
                        person_added.user.first_name = person_added.first_name
                        person_added.user.last_name = person_added.last_name
                        person_added.user.save()

                    messages.success(request, _('Person created successfully.'))
                    redirect_url = reverse("person_view", args=(person_added.id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"person_form": person_form,
               "user_form": user_form,
               "group_permissions": group_permissions,
               "creating": True,
               "can_change": True,
               "editing": True}

    return render(request, template_name, context)


def update_groups(person, list_groups):
    changed = False
    # remove old groups
    for group in person.user.groups.all():
        if group.id not in list_groups:
            person.user.groups = person.user.groups.exclude(id=group.id)
            changed = True
            person.user.save()

    # add new groups
    for item in list_groups:
        group = get_object_or_404(Group, pk=item)
        if group not in person.user.groups.all():
            person.user.groups.add(group)
            changed = True
    person.user.save()

    return changed


@login_required
@permission_required('team.change_team')
def person_view(request, person_id, template_name="team/person_register.html"):
    person = get_object_or_404(Person, pk=person_id)

    person_form = PersonRegisterForm(request.POST or None, instance=person)

    group_permissions = []

    if person.user:
        user_form = UserPersonForm(request.POST or None, instance=person.user)

        group_permissions = get_group_permissions(person)

    else:
        user_form = UserPersonForm(request.POST or None)

    for field in person_form.fields:
        person_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            have_user_to_remove = True if person.user else False

            person.delete()

            if have_user_to_remove:
                user = get_object_or_404(User, id=person.user_id)
                user.is_active = False
                user.save()

            messages.success(request, _('Person removed successfully.'))
            return redirect('person_list')
        else:
            messages.warning(request, _('Action not available.'))

    context = {"person": person,
               "person_form": person_form,
               'group_permissions': group_permissions,
               "user_form": user_form,
               "can_change": True,
               "editing": False}

    return render(request, template_name, context)


def get_group_permissions(person):
    group_permissions = []
    for group in Group.objects.all():
        checked = False
        if person.user:
            checked = group in person.user.groups.all()
        group_permissions.append(
            {'group': group,
             'checked': checked}
        )
    return group_permissions


@login_required
@permission_required('team.change_team')
def person_update(request, person_id, template_name="team/person_register.html"):
    person = get_object_or_404(Person, pk=person_id)

    person_form = PersonRegisterForm(request.POST or None, instance=person)

    user_form = UserPersonForm(request.POST or None, instance=person.user)
    # user_form = UserPersonForm(request.POST or None)

    # if person.user:
    #     user_form = UserPersonForm(request.POST or None, instance=person.user)
    # else:
    #     user_form = UserPersonForm(request.POST or None)
    group_permissions = get_group_permissions(person)

    if request.method == "POST":

        if request.POST['action'] == "save":
            if person_form.is_valid():

                changed = False
                error = False

                # TODO: error about user_form because always wait that the password.
                # example-1: if you only change the username
                # example-2: if you change some group selection, the "user_form.is_valid" is True

                if user_form.has_changed():
                    if user_form.is_valid():
                        person.user = user_form.save()
                        person.save()
                        changed = True
                    else:
                        error = True
                        messages.error(request,
                                       _('Error while updating person. Please correct the highlighted fields.'))

                if not error:
                    if person_form.has_changed():
                        person_form.save()
                        changed = True

                    if person.user:
                        if update_groups(person, [int(item) for item in request.POST.getlist('groups')]):
                            changed = True

                    if changed:
                        messages.success(request, _('Person updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("person_view", args=(person.id,))
                    return HttpResponseRedirect(redirect_url)

        if request.POST['action'] == "deactivate":
            user_to_deactivate = person.user
            person.user = None
            person.save()

            user_to_deactivate.is_active = False
            user_to_deactivate.save()
            messages.success(request, _('User deactivated successfully.'))

            redirect_url = reverse("person_view", args=(person.id,))
            return HttpResponseRedirect(redirect_url)

    context = {"person": person,
               "person_form": person_form,
               "user_form": user_form,
               "can_change": True,
               "group_permissions": group_permissions,
               "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def get_json_user_attributes(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    response_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'groups': [group.id for group in user.groups.all()]
    }

    return HttpResponse(json.dumps(response_data), content_type='application/json')


@login_required
@permission_required('team.change_team')
def team_list(request, template_name='team/team_list.html'):
    return render(request, template_name, context={"teams": Team.objects.all().order_by('name')})


@login_required
@permission_required('team.change_team')
def team_create(request, template_name="team/team_register.html"):

    team_form = TeamRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if team_form.is_valid():
                team_added = team_form.save()
                messages.success(request, _('Team created successfully.'))
                redirect_url = reverse("team_list", args=())
                return HttpResponseRedirect(redirect_url)
            else:
                messages.warning(request, _('Information not saved.'))
        else:
            messages.warning(request, _('Action not available.'))

    context = {"team_form": team_form,
               "creating": True,
               "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def team_view(request, team_id, template_name="team/team_register.html"):
    team = get_object_or_404(Team, pk=team_id)
    # team_person = get_object_or_404(Team, pk=team_person_id)

    team_form = TeamRegisterForm(request.POST or None, instance=team)
    team_person_form = TeamPersonRegisterForm(request.POST or None, initial={'team': team})

    for field in team_form.fields:
        team_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":

        if request.POST['action'][:7] == "change-":
            team_person = get_object_or_404(TeamPerson, pk=request.POST['action'][7:])
            try:
                team_person.is_coordinator = not team_person.is_coordinator
                team_person.save()
                messages.success(request, _('Is coordinator status successfully changed.'))
            except ProtectedError:
                messages.error(request, _("Error trying to the status of the coordinator."))
            redirect_url = reverse("team_view", args=(team_id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST['action'][:7] == "remove-":
            team_person = get_object_or_404(TeamPerson, pk=request.POST['action'][7:])
            try:
                team_person.delete()
                messages.success(request, _('Person removed successfully from the Team.'))
            except ProtectedError:
                messages.error(request, _("Error trying to delete a persom from the team."))
            redirect_url = reverse("team_view", args=(team_id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST['action'] == "remove":

            try:
                team.delete()
                messages.success(request, _('Team removed successfully.'))
                return redirect('team_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete a team."))
                redirect_url = reverse("team_view", args=(team_id,))
                return HttpResponseRedirect(redirect_url)

        if request.POST['action'] == "insert_new":
            if team_person_form.is_valid():
                team_person_added = team_person_form.save(commit=False)
                team_person_added.team = team
                team_person_added.save()
                messages.success(request, _('Person added to the team successfully.'))
                redirect_url = reverse("team_view", args=(team_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "team": team,
               "team_form": team_form,
               "team_person_form": team_person_form}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def team_update(request, team_id, template_name="team/team_register.html"):
    team = get_object_or_404(Team, pk=team_id)

    team_form = TeamRegisterForm(request.POST or None, instance=team)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if team_form.is_valid():
                if team_form.has_changed():
                    team_form.save()
                    messages.success(request, _('Team updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("team_view", args=(team.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"team": team,
               "team_form": team_form,
               "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('team.add_team')
def team_person_create(request, team_id, template_name="team/team_person_register.html"):
    team = get_object_or_404(Team, pk=team_id)
    team_person_form = TeamPersonRegisterForm(request.POST or None)
    if request.method == "POST":
        if request.POST['action'] == "save":
            if team_person_form.is_valid():
                person_added = team_person_form.save(commit=False)
                person_added.team = team
                person_added.save()
                messages.success(request, _('Team person created successfully.'))
                redirect_url = reverse("team_view", args=(person_added.team.id,))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.warning(request, _('Information not saved.'))
        else:
            messages.warning(request, _('Action not available.'))

    context = {"team_person_form": team_person_form,
               "team": team,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)
