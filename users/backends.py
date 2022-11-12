from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = get_user_model().objects.get(email=username)

        except User.DoesNotExist:
            return None
        if getattr(user, "is_active") and user.check_password():
            return user

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return get_user_model().objects.get(pk=user_id)

        except User.DoesNotExist:
            return None
