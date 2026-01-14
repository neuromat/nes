# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from custom_user.forms import InstitutionForm, UserForm, UserFormUpdate, UserProfileForm, ResearcherForm
from custom_user.models import Institution, UserProfile


def get_group_permissions(user):
    group_permissions = []
    for group in Group.objects.all():
        checked = False
        if user:
            checked = group in user.groups.all()
        group_permissions.append(
            {"group": group,
             "checked": checked}
        )
    return group_permissions


@login_required
@permission_required('auth.add_user')
def user_list(request, template_name='custom_user/initial_page.html'):
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    institutions = Institution.objects.all().order_by('name')
    data = {
        "object_list": users,
        "current_user_id": request.user.id,
        "institutions": institutions,
    }
    return render(request, template_name, data)


@login_required
@permission_required('auth.add_user')
def user_create(request, template_name='custom_user/register_users.html'):
    form = UserForm(request.POST or None)
    profile_form = UserProfileForm(request.POST or None)
    group_permissions = []
    groups = Group.objects.all()

    for group in groups:
        group_permissions.append(
            {"group": group,
             "checked": False}
        )

    if request.method == "POST":
        if request.POST['action'] == "save" and request.POST['login_enabled'] == 'True':
            if not User.objects.filter(email=request.POST['email']).exists():
                if form.is_valid() and profile_form.is_valid():
                    user = form.save()
                    profile = UserProfileForm(request.POST or None, instance=user.user_profile)
                    user.save()
                    profile.save()
                    messages.success(request, _('Researcher created successfully.'))
                    redirect_url = reverse("user_view", args=(user.pk,))
                    return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request,
                               _('A researcher with this email address has already been registered before. '
                                 'Please contact your system administrator if you want to reactivate this account.'))
                return redirect('user_new')

        if request.POST['action'] == "save" and request.POST['login_enabled'] == 'False':
            if not User.objects.filter(email=request.POST['email']).exists():
                researcher_form = ResearcherForm(request.POST or None)
                if researcher_form.is_valid():
                    new_reserch = researcher_form.save(commit=False)
                    new_reserch.username = new_reserch.email
                    new_reserch.save()
                    profile = UserProfileForm(request.POST or None, instance=new_reserch.user_profile)
                    profile.save()
                    messages.success(request, _('Researcher created successfully.'))
                    redirect_url = reverse("user_view", args=(new_reserch.pk,))
                    return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request,
                               _('A researcher with this email address has already been registered before. '
                                 'Please contact your system administrator if you want to reactivate this account.'))
                return redirect('user_new')

    context = {
        "form": form,
        "profile_form": profile_form,
        "group_permissions": group_permissions,
        "creating": True
    }

    return render(request, template_name, context)


@login_required
@permission_required('auth.change_user')
def user_view(request, user_id, template_name="custom_user/register_users.html"):
    user = get_object_or_404(User, pk=user_id)
    form = UserFormUpdate(request.POST or None, instance=user)
    profile_form = UserProfileForm(request.POST or None, instance=user.user_profile)
    group_permissions = get_group_permissions(user)

    for field in form.fields:
        form.fields[field].widget.attrs['disabled'] = True

    for field in profile_form.fields:
        profile_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            user.is_active = False
            user.save()
            messages.success(request, _('Researcher removed successfully.'))
            return redirect('user_list')

    context = {
        "user": user.id,
        "profile_form": profile_form,
        "form": form,
        "group_permissions": group_permissions,
        "viewing": True,
        "editing": False,
        "creating": False,
        "can_change": True,
        "current_user_id": request.user.id
    }

    return render(request, template_name, context)


@login_required
@permission_required('auth.change_user')
def user_update(request, user_id, template_name="custom_user/register_users.html"):
    user = get_object_or_404(User, pk=user_id)

    if user and user.is_active:
        form = UserFormUpdate(request.POST or None, instance=user)
        profile_form = UserProfileForm(request.POST or None, instance=user.user_profile)
        group_permissions = get_group_permissions(user)

        if request.method == "POST":
            if request.POST['action'] == "save" and request.POST['login_enabled'] == 'True':
                if form.is_valid() and profile_form.is_valid():
                    form.save()
                    profile_form.save()

                    if 'password_flag' in request.POST:
                        if request.POST['password']:
                            user = get_object_or_404(User, id=user_id)
                            profile, created = UserProfile.objects.get_or_create(user=user)
                            profile.force_password_change = True
                            profile.save()

                    messages.success(request, _('Researcher updated successfully.'))
                    redirect_url = reverse("user_view", args=(user_id,))
                    return HttpResponseRedirect(redirect_url)

            if request.POST['action'] == "save" and request.POST['login_enabled'] == 'False':
                researcher_form = ResearcherForm(request.POST or None, instance=user)

                if researcher_form.is_valid():
                    if researcher_form.has_changed() or profile_form.has_changed():
                        if 'email' in researcher_form.changed_data and \
                                User.objects.filter(email=request.POST['email']).exists():
                            messages.error(request, _('E-mail already registered'))
                            redirect_url = reverse("user_view", args=(user_id,))
                            return HttpResponseRedirect(redirect_url)
                        else:
                            researcher_form.save()
                            profile_form.save()
                            messages.success(request, _('Researcher updated successfully.'))
                            redirect_url = reverse("user_view", args=(user_id,))
                            return HttpResponseRedirect(redirect_url)
                    else:
                        messages.info(request, _('There is no changes to save.'))
                        redirect_url = reverse("user_view", args=(user_id,))
                        return HttpResponseRedirect(redirect_url)

            if request.POST['action'] == "remove":
                user = get_object_or_404(User, id=user_id)
                user.is_active = False
                user.save()
                messages.success(request, _('Researcher deleted successfully.'))
                return redirect('user_list')

            if request.POST['action'] == "deactivate":
                user = get_object_or_404(User, id=user_id)
                user.set_unusable_password()
                user.save()
                if profile_form.is_valid():
                    profile_form.save()
                messages.success(request, _('Researcher disabled successfully.'))
                redirect_url = reverse("user_view", args=(user_id,))
                return HttpResponseRedirect(redirect_url)

        context = {
            "user": user_id,
            "form": form,
            "profile_form": profile_form,
            "editing": True,
            "group_permissions": group_permissions,
            "creating": False,
            "current_user_id": request.user.id
        }

        return render(request, template_name, context)


@login_required
def institution_create(request, template_name="custom_user/institution_register.html"):
    institution_form = InstitutionForm(request.POST or None)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if institution_form.is_valid():
                institution = institution_form.save()
                messages.success(request, _('Institution created successfully.'))
                redirect_url = reverse("institution_view", args=(institution.id,))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.warning(request, _('Information not saved.'))
        else:
            messages.warning(request, _('Action not available.'))

    context = {"institution_form": institution_form,
               "creating": True,
               "editing": True}

    return render(request, template_name, context)


@login_required
def institution_view(request, institution_id, template_name="custom_user/institution_register.html"):
    institution = get_object_or_404(Institution, pk=institution_id)

    institution_form = InstitutionForm(request.POST or None, instance=institution)

    for field in institution_form.fields:
        institution_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            institution_used = UserProfile.objects.filter(institution=institution)
            if institution_used.exists():
                messages.warning(
                    request, _('This institution cannot be removed because there are researchers associated with it.')
                )

                redirect_url = reverse("institution_view", args=(institution_id,))
                return HttpResponseRedirect(redirect_url)

            if Institution.objects.filter(parent_id=institution_id).exists():
                messages.warning(request, _('This institution cannot be removed because there is (are) other '
                                            'institution(s) associated with it.'))

                redirect_url = reverse("institution_view", args=(institution_id,))
                return HttpResponseRedirect(redirect_url)

            institution.delete()
            messages.success(request, _('Institution removed successfully.'))
            redirect_url = reverse("user_list")
            return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "institution": institution,
               "institution_form": institution_form,
               "show_institution": True}

    return render(request, template_name, context)


@login_required
def institution_update(request, institution_id, template_name="custom_user/institution_register.html"):
    institution = get_object_or_404(Institution, pk=institution_id)

    institution_form = InstitutionForm(request.POST or None, instance=institution)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if institution_form.is_valid():
                if institution_form.has_changed():
                    institution_form.save()
                    messages.success(request, _('Institution updated successfully.'))
                else:
                    messages.info(request, _('There is no changes to save.'))

                redirect_url = reverse("institution_view", args=(institution_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"institution": institution,
               "institution_form": institution_form,
               "editing": True}

    return render(request, template_name, context)
