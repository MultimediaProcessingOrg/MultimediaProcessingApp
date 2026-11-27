from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):

    message = "Brak uprawnień do tego zasobu."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_admin_role", False):
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner is not None and owner == user

class IsAdminRole(permissions.BasePermission):
    message = "Wymagana rola ADMIN."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_admin_role", False))
