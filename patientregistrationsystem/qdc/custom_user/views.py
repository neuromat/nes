# coding=utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from custom_user.forms import UserForm, UserFormUpdate

from django.contrib import messages

from django.contrib.auth.models import User, Group

from django.utils.translation import ugettext as _

from custom_user.models import UserProfile


@login_required
@permission_required('auth.add_user')
def user_list(request, template_name='custom_user/user_list.html'):
    users = User.objects.filter(is_active=True).order_by('username')
    data = {'object_list': users, 'current_user_id': request.user.id}
    return render(request, template_name, data)


@login_required
@permission_required('auth.add_user')
def user_create(request, template_name='custom_user/register_users.html'):
    form = UserForm(request.POST or None)
    group_permissions = []
    groups = Group.objects.all()

    for group in groups:
        group_permissions.append(
            {'group': group,
             'checked': False}
        )

    if request.method == "POST":
        if request.POST['action'] == "save":
            if form.is_valid():
                form.save()
                messages.success(request, _('User created successfully.'))
                return redirect('user_list')
            else:
                messages.error(request, _('It was not possible to create user.'))
                if 'username' in form.errors:
                    try:
                        form.errors['username'].remove('Usuário com este Usuário já existe.')
                        if User.objects.get_by_natural_key(request.POST['username']).is_active:
                            form.errors['username'] = [_('This user name already exists.')]
                        else:
                            form.errors['username'] = [_('This username already exists in an disabled user.')]
                    except ValueError:
                        None
    return render(request, template_name, {'form': form, 'group_permissions': group_permissions, 'creating': True})


@login_required
@permission_required('auth.change_user')
def user_update(request, user_id, template_name="custom_user/register_users.html"):

    user = get_object_or_404(User, pk=user_id)

    if user and user.is_active:
        form = UserFormUpdate(request.POST or None, instance=user)
        user_groups = User.objects.get(id=user_id).groups.all()
        group_permissions = []
        groups = Group.objects.all()

        for group in groups:
            if group in user_groups:
                group_permissions.append(
                    {'group': group,
                     'checked': True}
                )
            else:
                group_permissions.append(
                    {'group': group,
                     'checked': False}
                )

        if request.method == "POST":
            if request.POST['action'] == "save":
                if form.is_valid():

                    form.save()

                    if request.POST['password']:
                        user = get_object_or_404(User, id=user_id)
                        profile, created = UserProfile.objects.get_or_create(user=user)
                        profile.force_password_change = True
                        profile.save()

                    messages.success(request, _('User updated successfully.'))
                    return redirect('user_list')

            else:
                if request.POST['action'] == "remove":
                    user = get_object_or_404(User, id=user_id)
                    user.is_active = False
                    user.save()
                    messages.success(request, _('User deleted successfully.'))

                    return redirect('user_list')

        context = {
            'form': form,
            'editing': True,
            'group_permissions': group_permissions,
            'creating': False
        }

        return render(request, template_name, context)
