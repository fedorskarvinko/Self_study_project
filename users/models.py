from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_TEACHER = "teacher"
    ROLE_STUDENT = "student"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Администратор"),
        (ROLE_TEACHER, "Преподаватель"),
        (ROLE_STUDENT, "Студент"),
    ]

    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={
            "unique": "Пользователь с таким email уже существует.",
        },
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        verbose_name="Роль",
        help_text="Определяет права доступа пользователя",
    )

    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="Аватар")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT
