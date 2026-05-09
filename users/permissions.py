from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Доступ только для администраторов"""

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.is_admin
        )


class IsTeacherUser(permissions.BasePermission):
    """Доступ для преподавателей и администраторов"""

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                (request.user.is_teacher or request.user.is_admin)
        )