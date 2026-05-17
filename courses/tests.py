from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from .models import Answer, Course, Lesson, Question, Test, UserTestResult

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )

    def test_create_course(self):
        course = Course.objects.create(
            title="Python", description="Learn Python", owner=self.teacher
        )
        self.assertEqual(str(course), "Python")
        self.assertEqual(course.lessons_count, 0)

    def test_lessons_count(self):
        course = Course.objects.create(title="Python", description="Desc", owner=self.teacher)
        Lesson.objects.create(title="L1", content="C1", course=course, order=1)
        Lesson.objects.create(title="L2", content="C2", course=course, order=2)
        self.assertEqual(course.lessons_count, 2)

    def test_is_published_default(self):
        course = Course.objects.create(title="Python", description="Desc", owner=self.teacher)
        self.assertFalse(course.is_published)


class LessonModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.course = Course.objects.create(title="Course", description="Desc", owner=self.teacher)

    def test_create_lesson(self):
        lesson = Lesson.objects.create(
            title="Lesson 1", content="Content", course=self.course, order=1
        )
        self.assertIn("Lesson 1", str(lesson))
        self.assertEqual(lesson.order, 1)

    def test_video_url_optional(self):
        lesson = Lesson.objects.create(title="Lesson", content="Content", course=self.course)
        self.assertIsNone(lesson.video_url)


class TestModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.course = Course.objects.create(title="Course", description="Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(title="Lesson", content="Content", course=self.course)
        self.test = Test.objects.create(title="Test", lesson=self.lesson, passing_score=80)

    def test_create_test(self):
        self.assertEqual(self.test.passing_score, 80)
        self.assertIn("Test", str(self.test))

    def test_questions_count(self):
        q1 = Question.objects.create(test=self.test, text="Q1")
        q2 = Question.objects.create(test=self.test, text="Q2")
        self.assertEqual(self.test.questions_count, 2)


class QuestionAnswerTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.course = Course.objects.create(title="Course", description="Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(title="Lesson", content="Content", course=self.course)
        self.test = Test.objects.create(title="Test", lesson=self.lesson)
        self.question = Question.objects.create(test=self.test, text="Q?", question_type="single")

    def test_create_answers(self):
        Answer.objects.create(question=self.question, text="A1", is_correct=True)
        Answer.objects.create(question=self.question, text="A2", is_correct=False)
        self.assertEqual(self.question.answers.count(), 2)

    def test_correct_answer_str(self):
        a = Answer.objects.create(question=self.question, text="Correct", is_correct=True)
        self.assertIn("✓", str(a))

    def test_wrong_answer_str(self):
        a = Answer.objects.create(question=self.question, text="Wrong", is_correct=False)
        self.assertIn("✗", str(a))


class UserTestResultTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="123", role="student"
        )
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.course = Course.objects.create(title="Course", description="Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(title="Lesson", content="Content", course=self.course)
        self.test = Test.objects.create(title="Test", lesson=self.lesson, passing_score=70)

    def test_result_passed(self):
        result = UserTestResult.objects.create(
            user=self.student, test=self.test, score=80, correct_answers=8, total_questions=10
        )
        self.assertTrue(result.is_passed)

    def test_result_failed(self):
        result = UserTestResult.objects.create(
            user=self.student, test=self.test, score=60, correct_answers=6, total_questions=10
        )
        self.assertFalse(result.is_passed)


class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="123", role="student"
        )

    def _get_token(self, username, password):
        response = self.client.post(
            "/api/auth/token/", {"username": username, "password": password}, format="json"
        )
        return response.data["access"]

    def test_create_course_as_teacher(self):
        token = self._get_token("teacher", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            "/api/courses/",
            {"title": "Python", "description": "Learn Python", "is_published": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_course(self):
        token = self._get_token("student", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post(
            "/api/courses/", {"title": "Python", "description": "Learn Python"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_courses_as_student(self):
        Course.objects.create(
            title="Published", description="D", owner=self.teacher, is_published=True
        )
        Course.objects.create(
            title="Hidden", description="D", owner=self.teacher, is_published=False
        )

        token = self._get_token("student", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF пагинация: ответ в response.data['results']
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    def test_get_course_detail(self):
        course = Course.objects.create(
            title="Python", description="Desc", owner=self.teacher, is_published=True
        )
        token = self._get_token("student", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/courses/{course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Python")

    def test_update_course(self):
        course = Course.objects.create(title="Old", description="Desc", owner=self.teacher)
        token = self._get_token("teacher", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.patch(f"/api/courses/{course.id}/", {"title": "New"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "New")

    def test_delete_course(self):
        course = Course.objects.create(title="To Delete", description="Desc", owner=self.teacher)
        token = self._get_token("teacher", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.delete(f"/api/courses/{course.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class LessonAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.course = Course.objects.create(title="Course", description="Desc", owner=self.teacher)

    def _get_token(self):
        response = self.client.post(
            "/api/auth/token/", {"username": "teacher", "password": "123"}, format="json"
        )
        return response.data["access"]

    def test_create_lesson(self):
        token = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            "/api/lessons/",
            {"title": "Lesson 1", "content": "Content", "course": self.course.id, "order": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_lessons(self):
        Lesson.objects.create(title="L1", content="C1", course=self.course, order=1)
        token = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="123", role="teacher"
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="123", role="student"
        )
        self.course = Course.objects.create(
            title="Course", description="Desc", owner=self.teacher, is_published=True
        )
        self.lesson = Lesson.objects.create(title="Lesson", content="Content", course=self.course)
        self.test = Test.objects.create(title="Test", lesson=self.lesson, passing_score=50)
        self.question = Question.objects.create(
            test=self.test, text="2+2=?", question_type="single"
        )
        Answer.objects.create(question=self.question, text="4", is_correct=True)
        Answer.objects.create(question=self.question, text="5", is_correct=False)

    def _get_token(self, username, password):
        response = self.client.post(
            "/api/auth/token/", {"username": username, "password": password}, format="json"
        )
        return response.data["access"]

    def test_create_test(self):
        self.assertEqual(self.test.passing_score, 50)
        self.assertIsNotNone(self.test.id)

    def test_add_question(self):
        token = self._get_token("teacher", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            f"/api/tests/{self.test.id}/add_question/",
            {
                "text": "New question?",
                "question_type": "single",
                "answers": [
                    {"text": "Yes", "is_correct": True},
                    {"text": "No", "is_correct": False},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_test_as_student(self):
        token = self._get_token("student", "123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(f"/api/tests/{self.test.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result_created(self):
        result = UserTestResult.objects.create(
            user=self.student, test=self.test, score=100, correct_answers=1, total_questions=1
        )
        self.assertTrue(result.is_passed)
