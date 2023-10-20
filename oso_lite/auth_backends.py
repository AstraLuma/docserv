from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import PermissionDenied
from .oso import Oso


class OsoBackend(BaseBackend):  # BaseBackend was added in Django 3.0
    """
    Handles authorization against Oso.
    """

    #: If True (default), super users will skip Oso authorization
    # (This is true as a simple default--makes it easier to develop initially)
    superuser_bypass = True

    #: If True (not default), this will block additional backends from attempting
    #: authorization.
    block_additional_backends = False

    def get_user_permissions(self, user_obj, obj=None):
        # Do nothing because we can't ask Polar this question
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        # Do nothing because we can't ask Polar this question
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        # This is assumed to have the similar semantics as has_perm():
        # * If obj is given, return the perms for this object
        # * If obj is None, return the perms the user has unconditionally
        perms = Oso.get_allowed_actions(user_obj, obj, allow_wildcard=True)
        if '*' in perms:
            # TODO: Query django for defined permissions
            perms.remove('*')
        return perms

    def has_module_perms(self, user_obj, app_label):
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        # TODO: This needs to query Polar if the user has any f"{app_label}.*"
        # permission for some object.
        # That is, `allow(user_obj, f"{app_label}.*", *)`
        ...

    def with_perm(self, perm, is_active=True, include_superusers=True, obj=None):
        """
        Return users that have permission "perm". By default, filter out
        inactive users and include superusers.
        """
        # TODO: This needs to perform an ORM query against the polar query `allow(*, perm, obj)`
        ...

    def has_perm(self, user_obj, perm, obj=None):
        if self.superuser_bypass and user_obj.is_superuser:
            return True

        # Perm will be in django's standard 'app.action_model' form
        if Oso.is_allowed(user_obj, perm, obj):
            # Authorized
            return True
        else:
            if self.block_additional_backends:
                raise PermissionDenied()
            else:
                return False


class OsoBackend_Nice(OsoBackend):
    """
    Handles authorization against Oso.

    Authorization will be fall through to other backends.
    """
    block_additional_backends = False


class OsoBackend_Complete(OsoBackend):
    """
    Handles authorization against Oso.

    Authorization will be blocked from other backends.
    """
    block_additional_backends = True
