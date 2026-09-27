"""
Scheduler Serializers
"""
from rest_framework import serializers
from .models import StudyPlan, StudySession
from apps.timetable.serializers import CourseSerializer


class StudySessionSerializer(serializers.ModelSerializer):
    """Study session serializer"""
    course = CourseSerializer(read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = StudySession
        fields = [
            'id', 'study_plan', 'course', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'duration_minutes',
            'session_type', 'topic', 'notes',
            'priority_score', 'difficulty_weight',
            'is_completed', 'actual_duration_minutes',
            'completion_notes', 'completed_at', 'created_at'
        ]


class StudyPlanSerializer(serializers.ModelSerializer):
    """Study plan serializer with sessions"""
    sessions = StudySessionSerializer(many=True, read_only=True)
    session_count = serializers.IntegerField(source='sessions.count', read_only=True)
    total_study_hours = serializers.SerializerMethodField()

    class Meta:
        model = StudyPlan
        fields = [
            'id', 'student', 'name', 'week_start', 'week_end',
            'status', 'generation_time_ms', 'optimization_score',
            'sessions', 'session_count', 'total_study_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['student']

    def get_total_study_hours(self, obj):
        total = sum(s.duration_minutes for s in obj.sessions.all())
        return round(total / 60, 2)
