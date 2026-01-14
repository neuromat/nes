from django.urls import reverse

from custom_user.models import UserProfile
import re
from django.shortcuts import redirect


class PasswordChangeMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not re.match(r'^/password_change/?', request.path)
            and not re.match(r'^/logout/?', request.path)
            and not request.user.is_superuser
        ):
            zm, created = UserProfile.objects.get_or_create(user=request.user)
            if zm.force_password_change:
                return redirect(reverse('password_change'))

        return self.get_response(request)
