from django.urls import path

from .views import CourseViewSet, LessonViewSet, TestViewSet, UserTestResultViewSet

urlpatterns = [
    # Курсы
    path("courses/", CourseViewSet.as_view({"get": "list", "post": "create"}), name="course-list"),
    path(
        "courses/<int:pk>/",
        CourseViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="course-detail",
    ),
    path(
        "courses/<int:pk>/lessons/",
        CourseViewSet.as_view({"get": "lessons"}),
        name="course-lessons",
    ),
    # Уроки
    path("lessons/", LessonViewSet.as_view({"get": "list", "post": "create"}), name="lesson-list"),
    path(
        "lessons/<int:pk>/",
        LessonViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="lesson-detail",
    ),
    path(
        "lessons/<int:pk>/add_test/",
        LessonViewSet.as_view({"post": "add_test"}),
        name="lesson-add-test",
    ),
    # Тесты
    path("tests/", TestViewSet.as_view({"get": "list", "post": "create"}), name="test-list"),
    path(
        "tests/<int:pk>/",
        TestViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="test-detail",
    ),
    path(
        "tests/<int:pk>/add_question/",
        TestViewSet.as_view({"post": "add_question"}),
        name="test-add-question",
    ),
    path(
        "tests/<int:pk>/submit_answers/",
        TestViewSet.as_view({"post": "submit_answers"}),
        name="test-submit-answers",
    ),
    # Результаты
    path("results/", UserTestResultViewSet.as_view({"get": "list"}), name="result-list"),
    path(
        "results/<int:pk>/",
        UserTestResultViewSet.as_view({"get": "retrieve"}),
        name="result-detail",
    ),
    path(
        "results/my_stats/",
        UserTestResultViewSet.as_view({"get": "my_stats"}),
        name="result-my-stats",
    ),
]
