"""
Attendance Serializers
"""
from rest_framework import serializers
from .models import AttendanceRecord, AttendanceSummary
from apps.timetable.serializers import CourseSerializer, ClassScheduleSerializer


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Attendance record serializer"""
    class_schedule = ClassScheduleSerializer(read_only=True)
    course_name = serializers.CharField(source='class_schedule.course.name', read_only=True)
    course_code = serializers.CharField(source='class_schedule.course.code', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'student', 'class_schedule', 'course_name', 'course_code',
            'date', 'status', 'check_in_time', 'check_out_time',
            'minutes_late', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student']


class AttendanceSummarySerializer(serializers.ModelSerializer):
    """Attendance summary serializer"""
    course = CourseSerializer(read_only=True)
    status = serializers.SerializerMethodField()
    sessions_needed_for_minimum = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSummary
        fields = [
            'id', 'student', 'course', 'total_sessions',
            'present_count', 'absent_count', 'late_count', 'excused_count',
            'attendance_percentage', 'minimum_required_percentage',
            'warning_threshold_percentage', 'status',
            'sessions_needed_for_minimum', 'warning_count',
            'last_warning_sent', 'updated_at'
        ]

    def get_status(self, obj):
        if obj.is_below_minimum:
            return 'critical'
        elif obj.is_near_threshold:
            return 'warning'
        return 'good'

    def get_sessions_needed_for_minimum(self, obj):
        """Calculate how many consecutive sessions needed to reach minimum"""
        if obj.attendance_percentage >= obj.minimum_required_percentage:
            return 0

        # Formula: solve for x in (present + x) / (total + x) >= minimum
        present = obj.present_count + obj.late_count
        total = obj.total_sessions - obj.excused_count
        minimum = obj.minimum_required_percentage / 100

        if total == 0:
            return 1

        needed = (minimum * total - present) / (1 - minimum)
        return max(1, int(needed) + 1)
