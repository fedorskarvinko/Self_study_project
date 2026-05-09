from rest_framework import serializers
from .models import Course, Lesson, Test, Question, Answer, UserTestResult


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для вариантов ответов (для преподавателей и админов)"""

    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'explanation']
        read_only_fields = ['id']


class AnswerForStudentSerializer(serializers.ModelSerializer):
    """Сериализатор ответов для студентов (без флага is_correct)"""

    class Meta:
        model = Answer
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов с ответами (для преподавателей и админов)"""
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'question_type',
            'order',
            'answers',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuestionForStudentSerializer(serializers.ModelSerializer):
    """Сериализатор вопросов для студентов (скрывает правильные ответы)"""
    answers = AnswerForStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'answers']


class TestSerializer(serializers.ModelSerializer):
    """Сериализатор тестов (для преподавателей и админов)"""
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Test
        fields = [
            'id',
            'title',
            'description',
            'lesson',
            'questions',
            'questions_count',
            'passing_score',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'questions_count']


class TestForStudentSerializer(serializers.ModelSerializer):
    """Сериализатор тестов для студентов (без правильных ответов)"""
    questions = QuestionForStudentSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Test
        fields = [
            'id',
            'title',
            'description',
            'lesson',
            'questions',
            'questions_count',
            'passing_score'
        ]


class TestCheckSerializer(serializers.Serializer):
    """Сериализатор для проверки ответов теста"""
    answers = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(),
            help_text='Список ID выбранных ответов'
        ),
        help_text='Словарь {question_id: [answer_ids]}'
    )

    def validate_answers(self, value):
        """Проверка что ответы не пустые"""
        if not value:
            raise serializers.ValidationError("Необходимо предоставить ответы")
        return value


class LessonListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения уроков в списке (без полного контента)"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    tests_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'course',
            'course_title',
            'order',
            'video_url',
            'tests_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения урока"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    tests = TestSerializer(many=True, read_only=True)
    tests_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'content',
            'course',
            'course_title',
            'order',
            'video_url',
            'tests',
            'tests_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения курса"""
    lessons = LessonListSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(
        source='owner.get_full_name',
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'owner',
            'owner_name',
            'is_published',
            'lessons',
            'lessons_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class CourseCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового курса"""

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'is_published']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Автоматически назначаем владельцем текущего пользователя"""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class UserTestResultSerializer(serializers.ModelSerializer):
    """Сериализатор результатов тестирования"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    lesson_title = serializers.CharField(
        source='test.lesson.title',
        read_only=True
    )
    course_title = serializers.CharField(
        source='test.lesson.course.title',
        read_only=True
    )

    class Meta:
        model = UserTestResult
        fields = [
            'id',
            'user',
            'user_name',
            'test',
            'test_title',
            'lesson_title',
            'course_title',
            'score',
            'correct_answers',
            'total_questions',
            'is_passed',
            'completed_at'
        ]
        read_only_fields = ['id', 'user', 'is_passed', 'completed_at']