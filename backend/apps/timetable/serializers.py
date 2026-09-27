"""
Timetable Serializers
"""
from rest_framework import serializers
from .models import Course, ClassSchedule, StudentCourse, Assignment, ExamSchedule, Event, Participant


class CourseSerializer(serializers.ModelSerializer):
    """Course serializer"""

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'description', 'credits', 'course_type',
            'department', 'lecturer_name', 'lecturer_email',
            'difficulty_rating', 'estimated_study_hours_per_week',
            'created_at', 'updated_at'
        ]


class ClassScheduleSerializer(serializers.ModelSerializer):
    """Class schedule serializer with course details"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration = serializers.IntegerField(source='duration_minutes', read_only=True)

    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'course', 'course_id', 'session_type', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'venue', 'building', 'room_number',
            'is_recurring', 'start_date', 'end_date', 'specific_date',
            'duration', 'created_at'
        ]


class StudentCourseSerializer(serializers.ModelSerializer):
    """Student enrollment serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = StudentCourse
        fields = [
            'id', 'student', 'student_name', 'course', 'course_id',
            'semester', 'academic_year', 'enrollment_date',
            'personal_difficulty_rating', 'target_grade'
        ]
        read_only_fields = ['student', 'enrollment_date']


class AssignmentSerializer(serializers.ModelSerializer):
    """Assignment serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    priority_label = serializers.CharField(source='get_priority_display', read_only=True)
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'course', 'course_id', 'title', 'description',
            'assessment_type', 'due_date', 'weight_percentage',
            'priority', 'priority_label', 'estimated_hours',
            'days_until_due', 'created_at', 'updated_at'
        ]

    def get_days_until_due(self, obj):
        from datetime import datetime
        now = datetime.now()
        diff = obj.due_date - now
        return diff.days


class ParticipantSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Participant
        fields = ['id', 'event', 'student', 'student_name', 'name', 'email', 'status', 'added_at']
        read_only_fields = ['event', 'added_at']


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'owner', 'title', 'description', 'event_type', 'start_time', 'end_time', 'location', 'all_day', 'participants', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at', 'participants']

    def validate(self, attrs):
        if attrs.get('end_time') and attrs.get('start_time') and attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        return attrs


class ExamScheduleSerializer(serializers.ModelSerializer):
    """Exam schedule serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )

    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'course', 'course_id', 'exam_type', 'date',
            'start_time', 'end_time', 'venue', 'duration_minutes',
            'is_confirmed', 'created_at'
        ]
