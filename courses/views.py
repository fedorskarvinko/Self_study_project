from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Lesson, Test, UserTestResult
from .permissions import CanViewResults, IsCourseOwnerOrReadOnly
from .serializers import (
    AnswerSerializer,
    CourseCreateSerializer,
    CourseSerializer,
    LessonListSerializer,
    LessonSerializer,
    QuestionSerializer,
    TestCheckSerializer,
    TestForStudentSerializer,
    TestSerializer,
    UserTestResultSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы"""

    permission_classes = [permissions.IsAuthenticated, IsCourseOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return CourseCreateSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "student")

        if role == "admin":
            queryset = Course.objects.all()
        elif role == "teacher":
            queryset = Course.objects.filter(owner=user)
        else:
            queryset = Course.objects.filter(is_published=True)

        return queryset.select_related("owner")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def lessons(self, request, **kwargs):
        course = self.get_object()
        lessons = course.lessons.all().order_by("order")
        return Response(LessonListSerializer(lessons, many=True).data)


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки"""

    permission_classes = [permissions.IsAuthenticated, IsCourseOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return LessonListSerializer
        return LessonSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "student")

        if role == "admin":
            queryset = Lesson.objects.all()
        elif role == "teacher":
            queryset = Lesson.objects.filter(course__owner=user)
        else:
            queryset = Lesson.objects.filter(course__is_published=True)

        return queryset.select_related("course")

    @action(detail=True, methods=["post"])
    def add_test(self, request, **kwargs):
        lesson = self.get_object()
        serializer = TestSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestViewSet(viewsets.ModelViewSet):
    """Тесты"""

    permission_classes = [permissions.IsAuthenticated, IsCourseOwnerOrReadOnly]

    def get_serializer_class(self):
        role = getattr(self.request.user, "role", "student")
        if role == "student":
            return TestForStudentSerializer
        return TestSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "student")

        if role == "admin":
            queryset = Test.objects.all()
        elif role == "teacher":
            queryset = Test.objects.filter(lesson__course__owner=user)
        else:
            queryset = Test.objects.filter(lesson__course__is_published=True)

        return queryset.select_related("lesson__course")

    @action(detail=True, methods=["post"])
    def add_question(self, request, **kwargs):
        test = self.get_object()

        # Создаем вопрос
        question_serializer = QuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question = question_serializer.save(test=test)

            # Добавляем ответы
            answers_data = request.data.get("answers", [])
            for answer_data in answers_data:
                answer_serializer = AnswerSerializer(data=answer_data)
                if answer_serializer.is_valid():
                    answer_serializer.save(question=question)
                else:
                    question.delete()
                    return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def submit_answers(self, request, **kwargs):
        test = self.get_object()

        serializer = TestCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_answers = serializer.validated_data["answers"]
        questions = test.questions.all()

        correct_count = 0
        for question in questions:
            correct_ids = set(question.answers.filter(is_correct=True).values_list("id", flat=True))
            user_ids = set(user_answers.get(str(question.id), []))
            if user_ids == correct_ids:
                correct_count += 1

        total = questions.count()
        score = (correct_count / total * 100) if total > 0 else 0

        result = UserTestResult.objects.create(
            user=request.user,
            test=test,
            score=score,
            correct_answers=correct_count,
            total_questions=total,
        )

        return Response(
            {
                "score": round(score, 2),
                "correct_answers": correct_count,
                "total_questions": total,
                "is_passed": result.is_passed,
            }
        )


class UserTestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """Результаты тестов"""

    serializer_class = UserTestResultSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewResults]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", "student")

        if role == "admin":
            queryset = UserTestResult.objects.all()
        elif role == "teacher":
            queryset = UserTestResult.objects.filter(test__lesson__course__owner=user)
        else:
            queryset = UserTestResult.objects.filter(user=user)

        return queryset.select_related("user", "test")

    @action(detail=False, methods=["get"])
    def my_stats(self, request, **kwargs):
        results = UserTestResult.objects.filter(user=request.user)
        total = results.count()
        passed = results.filter(is_passed=True).count()

        return Response(
            {
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": total - passed,
            }
        )
