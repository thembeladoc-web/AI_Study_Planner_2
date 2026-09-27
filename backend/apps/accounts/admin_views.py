"""Admin-only API for the Pace AI Study Planner management dashboard."""
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import AttendanceRecordSerializer
from apps.study_groups.models import StudyGroup
from apps.study_groups.serializers import StudyGroupSerializer
from apps.timetable.models import Assignment, ClassSchedule, Course, ExamSchedule
from apps.timetable.serializers import (
    AssignmentSerializer,
    ClassScheduleSerializer,
    CourseSerializer,
    ExamScheduleSerializer,
)

Student = get_user_model()


class AdminStudentSerializer(serializers.ModelSerializer):
    """Admin-safe student representation with account controls."""
    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'student_number', 'program', 'year_of_study', 'is_active',
            'is_staff', 'is_superuser', 'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login', 'is_superuser']


class AdminStudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('-date_joined')
    serializer_class = AdminStudentSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_number']


class AdminCourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('code')
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]


class AdminScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.select_related('course').all()
    serializer_class = ClassScheduleSerializer
    permission_classes = [IsAdminUser]


class AdminAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('course').all().order_by('due_date')
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminUser]


class AdminExamViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.select_related('course').all().order_by('date', 'start_time')
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAdminUser]


class AdminStudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('course', 'created_by').all()
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAdminUser]


class AdminAttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        'student', 'class_schedule__course'
    ).all().order_by('-date')
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAdminUser]


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            'users': Student.objects.count(),
            'active_users': Student.objects.filter(is_active=True).count(),
            'staff_users': Student.objects.filter(is_staff=True).count(),
            'courses': Course.objects.count(),
            'schedules': ClassSchedule.objects.count(),
            'assignments': Assignment.objects.count(),
            'exams': ExamSchedule.objects.count(),
            'study_groups': StudyGroup.objects.count(),
            'attendance_records': AttendanceRecord.objects.count(),
            'group_statuses': list(
                StudyGroup.objects.values('status').annotate(total=Count('id')).order_by('status')
            ),
        })
