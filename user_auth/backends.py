from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        login_value = email or username
        if not login_value or not password:
            return None

        try:
            user = User.objects.get(email=login_value)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=login_value)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
