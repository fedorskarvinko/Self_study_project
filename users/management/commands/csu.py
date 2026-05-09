from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    """Создание суперпользователя (администратора)"""

    help = "Создание суперпользователя (администратора)"

    def handle(self, *args, **options):
        """
        Основной метод команды.
        Создаёт суперпользователя с предустановленными данными.
        """

        email = "admin@example.com"
        password = "123qwe"

        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser(email=email)
            user.set_password(password)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.role = "admin"
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f"Администратор {email} создан! Пароль: {password}")
            )
        else:
            self.stdout.write(self.style.WARNING(f"Пользователь {email} уже существует"))
