from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Allow login with email (stored as username) + password.
    Falls back to the standard username lookup so the admin still works.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' field on the login form contains whatever the user typed.
        # Try treating it as an email first (exact match, case-insensitive).
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # Also try matching against the email field itself
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
