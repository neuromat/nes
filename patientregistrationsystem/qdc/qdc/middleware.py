from django.http import HttpResponseRedirect
from quiz.models import UserProfile
import re
from django.shortcuts import redirect, get_object_or_404


class PasswordChangeMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated() and not re.match(r'^/password_change/?', request.path) and not re.match(
                r'^/logout/?', request.path) and not request.user.is_superuser:

            zm, created = UserProfile.objects.get_or_create(user=request.user)
            if zm.force_password_change:
                # return HttpResponseRedirect('/password_change/')
                return redirect('django.contrib.auth.views.password_change')
