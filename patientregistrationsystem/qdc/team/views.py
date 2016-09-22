from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _

from .forms import PersonRegisterForm
from .models import Person, Team


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
            'href': reverse("person_list", args=()),
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
