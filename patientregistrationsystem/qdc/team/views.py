# coding=utf-8

import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _

from .forms import PersonRegisterForm, TeamRegisterForm, TeamPersonRegisterForm
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

    if request.method == "POST":

        if request.POST['action'] == "save":

            if person_form.is_valid():

                person_added = person_form.save()

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
               "creating": True,
               "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def person_view(request, person_id, template_name="team/person_register.html"):
    person = get_object_or_404(Person, pk=person_id)

    person_form = PersonRegisterForm(request.POST or None, instance=person)

    for field in person_form.fields:
        person_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                person.delete()
                messages.success(request, _('Person removed successfully.'))
                return redirect('person_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete person."))
                redirect_url = reverse("person_view", args=(person_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "person": person,
               "person_form": person_form}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def person_update(request, person_id, template_name="team/person_register.html"):
    person = get_object_or_404(Person, pk=person_id)

    person_form = PersonRegisterForm(request.POST or None, instance=person)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if person_form.is_valid():
                if person_form.has_changed():
                    person_form.save()
                    messages.success(request, _('Person updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("person_view", args=(person.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"person": person,
               "person_form": person_form,
               "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('team.change_team')
def get_json_user_attributes(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    response_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
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

                # sync user
                # if person_added.user:
                #     person_added.user.first_name = person_added.first_name
                #     person_added.user.last_name = person_added.last_name
                #     person_added.user.save()

                messages.success(request, _('Team created successfully.'))
#                redirect_url = reverse("team_view", args=(team_added.id,))
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

    team_form = TeamRegisterForm(request.POST or None, instance=team)
    team_person_form = TeamPersonRegisterForm(request.POST or None, initial={'team': team})

    for field in team_form.fields:
        team_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
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



#############################

@login_required
@permission_required('team.team_person')
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
                # redirect_url = reverse("software_version_view", args=(version_added.id,))
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

#############################

