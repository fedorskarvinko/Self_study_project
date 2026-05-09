from rest_framework import permissions
from .models import Course


class IsCourseOwnerOrReadOnly(permissions.BasePermission):
    """
    Права доступа для курсов и уроков:
    - GET, HEAD, OPTIONS: доступны всем аутентифицированным
    - POST: доступен преподавателям и админам
    - PUT, PATCH, DELETE: доступны владельцу или админу
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return (
                request.user.is_authenticated and
                request.user.role in ['teacher', 'admin']
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Course):
            return obj.owner == request.user or request.user.role == 'admin'

        if hasattr(obj, 'course'):
            return obj.course.owner == request.user or request.user.role == 'admin'

        if hasattr(obj, 'test'):
            course_owner = obj.test.lesson.course.owner
            return course_owner == request.user or request.user.role == 'admin'

        if hasattr(obj, 'lesson'):
            course_owner = obj.lesson.course.owner
            return course_owner == request.user or request.user.role == 'admin'

        if hasattr(obj, 'question'):
            course_owner = obj.question.test.lesson.course.owner
            return course_owner == request.user or request.user.role == 'admin'

        return False


class CanSubmitTestAnswers(permissions.BasePermission):
    """Только студенты могут отправлять ответы на тесты"""

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.role == 'student'
        )


class CanViewResults(permissions.BasePermission):
    """
    Права на просмотр результатов:
    - Студент видит только свои
    - Преподаватель видит результаты своих тестов
    - Администратор видит все
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True

        if request.user.role == 'teacher':
            return obj.test.lesson.course.owner == request.user

        return obj.user == request.user