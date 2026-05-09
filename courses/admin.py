from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Test, Question, Answer, UserTestResult


class LessonInline(admin.TabularInline):
    """Встроенное отображение уроков внутри курса"""
    model = Lesson
    extra = 0
    fields = ['title', 'order', 'video_url', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True
    ordering = ['order']


class TestInline(admin.TabularInline):
    """Встроенное отображение тестов внутри урока"""
    model = Test
    extra = 0
    fields = ['title', 'passing_score', 'questions_count_display']
    readonly_fields = ['questions_count_display']
    show_change_link = True

    def questions_count_display(self, obj):
        """Отображение количества вопросов"""
        return obj.questions_count if obj.pk else 0

    questions_count_display.short_description = 'Вопросов'


class AnswerInline(admin.TabularInline):
    """Встроенное отображение ответов внутри вопроса"""
    model = Answer
    extra = 1
    fields = ['text', 'is_correct', 'explanation']
    min_num = 2  # Минимум 2 ответа


class QuestionInline(admin.TabularInline):
    """Встроенное отображение вопросов внутри теста"""
    model = Question
    extra = 0
    fields = ['text_preview', 'question_type', 'order']
    readonly_fields = ['text_preview']
    show_change_link = True
    ordering = ['order']

    def text_preview(self, obj):
        """Превью текста вопроса"""
        if obj.pk:
            return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
        return ''

    text_preview.short_description = 'Вопрос'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Административная панель для курсов"""

    list_display = [
        'title',
        'owner_full_name',
        'is_published_status',
        'lessons_count_display',
        'created_at'
    ]

    list_filter = [
        'is_published',
        'owner',
        'created_at'
    ]

    search_fields = [
        'title',
        'description',
        'owner__username',
        'owner__email'
    ]

    inlines = [LessonInline]

    readonly_fields = ['created_at', 'updated_at', 'owner']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'description'
            )
        }),
        ('Владелец и статус', {
            'fields': (
                'owner',
                'is_published'
            )
        }),
        ('Даты', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 20

    def owner_full_name(self, obj):
        """Полное имя владельца"""
        return obj.owner.get_full_name() or obj.owner.username

    owner_full_name.short_description = 'Автор'
    owner_full_name.admin_order_field = 'owner__last_name'

    def is_published_status(self, obj):
        """Статус публикации с иконкой"""
        if obj.is_published:
            return format_html(
                '<span style="color: green;">✓ Опубликован</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Не опубликован</span>'
        )

    is_published_status.short_description = 'Статус'

    def lessons_count_display(self, obj):
        """Количество уроков с ссылкой"""
        count = obj.lessons_count
        if count > 0:
            return format_html(
                '<b>{}</b> уроков'.format(count)
            )
        return 'Нет уроков'

    lessons_count_display.short_description = 'Уроки'

    def save_model(self, request, obj, form, change):
        """Автоматически назначаем владельца при создании"""
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Административная панель для уроков"""

    list_display = [
        'title',
        'course_link',
        'order',
        'tests_count_display',
        'has_video',
        'created_at'
    ]

    list_filter = [
        'course',
        'created_at'
    ]

    search_fields = [
        'title',
        'content',
        'course__title'
    ]

    list_editable = ['order']

    readonly_fields = ['created_at', 'updated_at']

    inlines = [TestInline]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'content',
                'course'
            )
        }),
        ('Дополнительно', {
            'fields': (
                'order',
                'video_url'
            )
        }),
        ('Даты', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 20

    def course_link(self, obj):
        """Ссылка на курс"""
        from django.urls import reverse
        url = reverse('admin:courses_course_change', args=[obj.course.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.course.title
        )

    course_link.short_description = 'Курс'
    course_link.admin_order_field = 'course__title'

    def tests_count_display(self, obj):
        """Количество тестов"""
        count = obj.tests_count if hasattr(obj, 'tests_count') else obj.tests.count()
        if count > 0:
            return format_html(
                '<b>{}</b> тестов'.format(count)
            )
        return 'Нет тестов'

    tests_count_display.short_description = 'Тесты'

    def has_video(self, obj):
        """Наличие видео"""
        if obj.video_url:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        return format_html(
            '<span style="color: gray;">✗</span>'
        )

    has_video.short_description = 'Видео'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Административная панель для тестов"""

    list_display = [
        'title',
        'lesson_link',
        'questions_count_display',
        'passing_score_display',
        'created_at'
    ]

    list_filter = [
        'lesson__course',
        'lesson',
        'created_at'
    ]

    search_fields = [
        'title',
        'description',
        'lesson__title'
    ]

    readonly_fields = ['created_at']

    inlines = [QuestionInline]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'description',
                'lesson'
            )
        }),
        ('Настройки проверки', {
            'fields': ('passing_score',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 20

    def lesson_link(self, obj):
        """Ссылка на урок"""
        from django.urls import reverse
        url = reverse('admin:courses_lesson_change', args=[obj.lesson.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.lesson.title
        )

    lesson_link.short_description = 'Урок'
    lesson_link.admin_order_field = 'lesson__title'

    def questions_count_display(self, obj):
        """Количество вопросов"""
        count = obj.questions_count if hasattr(obj, 'questions_count') else obj.questions.count()
        if count > 0:
            return format_html(
                '<b>{}</b> вопросов'.format(count)
            )
        return 'Нет вопросов'

    questions_count_display.short_description = 'Вопросы'

    def passing_score_display(self, obj):
        """Отображение проходного балла"""
        return f'{obj.passing_score}%'

    passing_score_display.short_description = 'Проходной балл'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Административная панель для вопросов"""

    list_display = [
        'text_preview',
        'test_link',
        'question_type_display',
        'order',
        'answers_count_display'
    ]

    list_filter = [
        'question_type',
        'test__lesson__course',
        'test'
    ]

    search_fields = [
        'text',
        'test__title'
    ]

    readonly_fields = ['created_at']

    inlines = [AnswerInline]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'text',
                'test',
                'question_type',
                'order'
            )
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 20

    def text_preview(self, obj):
        """Превью текста вопроса"""
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text

    text_preview.short_description = 'Текст вопроса'

    def test_link(self, obj):
        """Ссылка на тест"""
        from django.urls import reverse
        url = reverse('admin:courses_test_change', args=[obj.test.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.test.title
        )

    test_link.short_description = 'Тест'
    test_link.admin_order_field = 'test__title'

    def question_type_display(self, obj):
        """Тип вопроса с иконкой"""
        if obj.question_type == 'single':
            return format_html(
                '🔘 Одиночный выбор'
            )
        return format_html(
            '☑️ Множественный выбор'
        )

    question_type_display.short_description = 'Тип'

    def answers_count_display(self, obj):
        """Количество ответов"""
        count = obj.answers.count()
        correct = obj.answers.filter(is_correct=True).count()
        return format_html(
            '{} ответов ({} правильных)'.format(count, correct)
        )

    answers_count_display.short_description = 'Ответы'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Административная панель для ответов"""

    list_display = [
        'text_preview',
        'question_preview',
        'is_correct_display',
        'has_explanation'
    ]

    list_filter = [
        'is_correct',
        'question__test',
        'question'
    ]

    search_fields = [
        'text',
        'explanation',
        'question__text'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'question',
                'text',
                'is_correct'
            )
        }),
        ('Дополнительно', {
            'fields': ('explanation',)
        }),
    )

    list_per_page = 30

    def text_preview(self, obj):
        """Превью текста ответа"""
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text

    text_preview.short_description = 'Ответ'

    def question_preview(self, obj):
        """Превью вопроса"""
        return obj.question.text[:60] + '...' if len(obj.question.text) > 60 else obj.question.text

    question_preview.short_description = 'Вопрос'

    def is_correct_display(self, obj):
        """Статус правильности ответа"""
        if obj.is_correct:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Правильный</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Неправильный</span>'
        )

    is_correct_display.short_description = 'Статус'

    def has_explanation(self, obj):
        """Наличие пояснения"""
        if obj.explanation:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        return format_html(
            '<span style="color: gray;">✗</span>'
        )

    has_explanation.short_description = 'Пояснение'


@admin.register(UserTestResult)
class UserTestResultAdmin(admin.ModelAdmin):
    """Административная панель для результатов тестов"""

    list_display = [
        'user_info',
        'test_title',
        'score_display',
        'is_passed_status',
        'completed_at'
    ]

    list_filter = [
        'is_passed',
        'test__lesson__course',
        'test',
        'completed_at'
    ]

    search_fields = [
        'user__username',
        'user__email',
        'test__title'
    ]

    readonly_fields = [
        'user',
        'test',
        'score',
        'correct_answers',
        'total_questions',
        'is_passed',
        'completed_at'
    ]

    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('user',)
        }),
        ('Информация о тесте', {
            'fields': ('test',)
        }),
        ('Результаты', {
            'fields': (
                'score_display_field',
                'correct_answers',
                'total_questions',
                'is_passed_status_field'
            )
        }),
        ('Дата', {
            'fields': ('completed_at',)
        }),
    )

    list_per_page = 20

    def user_info(self, obj):
        """Информация о пользователе"""
        return format_html(
            '{} <br><small>{}</small>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )

    user_info.short_description = 'Пользователь'
    user_info.admin_order_field = 'user__username'

    def test_title(self, obj):
        """Название теста с уроком"""
        return format_html(
            '{}<br><small>Урок: {}</small>',
            obj.test.title,
            obj.test.lesson.title
        )

    test_title.short_description = 'Тест'
    test_title.admin_order_field = 'test__title'

    def score_display(self, obj):
        """Отображение результата"""
        color = 'green' if obj.is_passed else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span> '
            '<small>({}/{})</small>',
            color,
            obj.score,
            obj.correct_answers,
            obj.total_questions
        )

    score_display.short_description = 'Результат'
    score_display.admin_order_field = 'score'

    def score_display_field(self, obj):
        """Поле результата для детального просмотра"""
        return format_html(
            '<b>Результат:</b> {}%<br>'
            '<b>Правильных ответов:</b> {} из {}<br>'
            '<b>Проходной балл:</b> {}%',
            obj.score,
            obj.correct_answers,
            obj.total_questions,
            obj.test.passing_score
        )

    score_display_field.short_description = 'Результат'

    def is_passed_status(self, obj):
        """Статус прохождения теста"""
        if obj.is_passed:
            return format_html(
                '<span style="color: green;">✓ Пройден</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Не пройден</span>'
        )

    is_passed_status.short_description = 'Статус'
    is_passed_status.admin_order_field = 'is_passed'

    def is_passed_status_field(self, obj):
        """Поле статуса для детального просмотра"""
        if obj.is_passed:
            return format_html(
                '<span style="color: green; font-size: 16px;">✓ Тест успешно пройден</span>'
            )
        return format_html(
            '<span style="color: red; font-size: 16px;">✗ Тест не пройден</span>'
        )

    is_passed_status_field.short_description = 'Статус прохождения'

    def has_add_permission(self, request):
        """Запрещаем ручное добавление результатов"""
        return False

    def has_change_permission(self, request, obj=None):
        """Запрещаем изменение результатов"""
        return False
