from django.core.exceptions import PermissionDenied


def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            profil = getattr(request.user, 'profilutilisateur', None)
            if profil and profil.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
