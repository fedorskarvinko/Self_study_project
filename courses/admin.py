from django.contrib import admin

from .models import Answer, Course, Lesson, Question, Test, UserTestResult


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["title", "order"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "is_published", "created_at"]
    list_filter = ["is_published", "created_at"]
    search_fields = ["title", "description"]
    inlines = [LessonInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "created_at"]
    list_filter = ["course"]
    search_fields = ["title"]


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "passing_score", "created_at"]
    list_filter = ["lesson__course"]
    search_fields = ["title"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text_preview", "test", "question_type"]
    list_filter = ["question_type", "test"]
    search_fields = ["text"]

    def text_preview(self, obj):
        if obj.text:
            return obj.text[:50]
        return ""

    text_preview.short_description = "Вопрос"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text_preview", "question", "is_correct"]
    list_filter = ["is_correct"]
    search_fields = ["text"]

    def text_preview(self, obj):
        if obj.text:
            return obj.text[:50]
        return ""

    text_preview.short_description = "Ответ"


@admin.register(UserTestResult)
class UserTestResultAdmin(admin.ModelAdmin):
    list_display = ["user", "test", "score", "is_passed", "completed_at"]
    list_filter = ["is_passed", "completed_at"]
    readonly_fields = [
        "user",
        "test",
        "score",
        "correct_answers",
        "total_questions",
        "completed_at",
    ]
