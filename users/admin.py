from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Расширенная админка для управления пользователями"""

    list_display = [
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    ]

    list_filter = ["role", "is_active", "is_staff", "is_superuser", "date_joined"]

    search_fields = ["username", "email", "first_name", "last_name", "bio"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name", "email", "role", "bio", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        (
            "Важные даты",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "date_joined", "last_login"]

    ordering = ["-date_joined"]

    list_per_page = 25

    actions = ["make_teacher", "make_student", "make_admin"]

    def make_teacher(self, request, queryset):
        """Массовое назначение роли преподавателя"""
        updated = queryset.update(role=CustomUser.ROLE_TEACHER)
        self.message_user(request, f"{updated} пользователей назначены преподавателями")

    make_teacher.short_description = "Назначить преподавателем"

    def make_student(self, request, queryset):
        """Массовое назначение роли студента"""
        updated = queryset.update(role=CustomUser.ROLE_STUDENT)
        self.message_user(request, f"{updated} пользователей назначены студентами")

    make_student.short_description = "Назначить студентом"

    def make_admin(self, request, queryset):
        """Массовое назначение роли администратора"""
        updated = queryset.update(role=CustomUser.ROLE_ADMIN, is_staff=True)
        self.message_user(request, f"{updated} пользователей назначены администраторами")

    make_admin.short_description = "Назначить администратором"

    def get_readonly_fields(self, request, obj=None):
        """Делаем некоторые поля только для чтения при редактировании"""
        readonly = list(self.readonly_fields)
        if obj:  # Редактирование существующего пользователя
            return readonly
        return []
