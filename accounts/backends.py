"""
Custom authentication backend to allow login with email (e.g. in Django admin).
If the identifier contains '@', look up user by email; otherwise use username.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email or username.
    When identifier contains '@', find user by email; otherwise by username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                User().set_password(password)  # run default hasher to limit timing attacks
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                User().set_password(password)
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
