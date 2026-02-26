from django.shortcuts import redirect
from django.urls import reverse


class MustChangePasswordMiddleware:
    """Redirect authenticated users to password change if `profile.must_change_password` is True."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # allow access to password change views, logout and admin
            allowed_paths = [
                reverse('auth:password_change'),
                reverse('auth:password_change_done'),
                reverse('auth:logout'),
                '/admin/',
            ]
            path = request.path
            try:
                must = getattr(user, 'profile', None) and user.profile.must_change_password
            except Exception:
                must = False

            if must and not any(path.startswith(p) for p in allowed_paths):
                return redirect('auth:password_change')

        return self.get_response(request)
