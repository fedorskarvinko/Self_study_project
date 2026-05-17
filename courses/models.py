from django.conf import settings
from django.db import models


class Course(models.Model):
    """Курс - основная единица обучения."""

    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание", help_text="Подробное описание курса")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Автор курса",
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def lessons_count(self):
        """Количество уроков в курсе"""
        return self.lessons.count()


class Lesson(models.Model):
    """Урок - отдельное занятие в курсе."""

    title = models.CharField(max_length=200, verbose_name="Название урока")
    content = models.TextField(verbose_name="Содержание", help_text="Текст урока")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["course", "order"]

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    @property
    def tests_count(self):
        """Количество тестов в уроке"""
        return self.tests.count()


class Test(models.Model):
    """Тест для проверки знаний по уроку."""

    title = models.CharField(max_length=200, verbose_name="Название теста")
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="tests", verbose_name="Урок"
    )
    description = models.TextField(blank=True, verbose_name="Описание теста")
    passing_score = models.PositiveIntegerField(
        default=70,
        verbose_name="Проходной балл (%)",
        help_text="Минимальный процент правильных ответов для прохождения",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return f"{self.title} - {self.lesson.title}"

    @property
    def questions_count(self):
        """Количество вопросов в тесте"""
        return self.questions.count()


class Question(models.Model):
    """Вопрос теста."""

    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, related_name="questions", verbose_name="Тест"
    )
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("single", "Одиночный выбор"),
            ("multiple", "Множественный выбор"),
        ],
        default="single",
        verbose_name="Тип вопроса",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["test", "order"]

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    """Вариант ответа на вопрос."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Вопрос"
    )
    text = models.CharField(max_length=500, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    explanation = models.TextField(blank=True, verbose_name="Пояснение к ответу")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f"{self.text[:30]} {'✓' if self.is_correct else '✗'}"


class UserTestResult(models.Model):
    """Результат прохождения теста пользователем."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_results",
        verbose_name="Пользователь",
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, related_name="results", verbose_name="Тест"
    )
    score = models.FloatField(verbose_name="Результат (%)")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Правильных ответов")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Всего вопросов")
    is_passed = models.BooleanField(default=False, verbose_name="Тест пройден")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время завершения")

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.score}%"

    def save(self, *args, **kwargs):
        """Автоматически определяем пройден ли тест"""
        if not self.is_passed:
            self.is_passed = self.score >= self.test.passing_score
        super().save(*args, **kwargs)
