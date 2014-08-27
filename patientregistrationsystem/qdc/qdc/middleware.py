
from django.http import HttpResponseRedirect

import re
from django.shortcuts import redirect


class PasswordChangeMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated() and not re.match(r'^/password_change/?', request.path) and not re.match(r'^/logout/?', request.path):

            profile = request.user.get_profile()
            if profile.force_password_change:
                #return HttpResponseRedirect('/password_change/')
                return redirect('django.contrib.auth.views.password_change')
