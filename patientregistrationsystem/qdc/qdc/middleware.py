import re

from custom_user.models import UserProfile
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class PasswordChangeMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        if (
            request.user.is_authenticated
            and not re.match(r"^/password_change/?", request.path)
            and not re.match(r"^/logout/?", request.path)
            and not request.user.is_superuser
        ):
            zm, created = UserProfile.objects.get_or_create(user=request.user)
            if zm.force_password_change:
                return redirect(reverse("password_change"))
