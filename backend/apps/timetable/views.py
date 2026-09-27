"""
Timetable Views
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from .models import Course, ClassSchedule, StudentCourse, Assignment, ExamSchedule, Event, Participant
from .serializers import (
    CourseSerializer, ClassScheduleSerializer, StudentCourseSerializer,
    AssignmentSerializer, ExamScheduleSerializer, EventSerializer, ParticipantSerializer
)


# ============ EVENTS AND PARTICIPANTS API ============

class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'all_day']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'end_time', 'created_at']

    def get_queryset(self):
        return Event.objects.filter(
            Q(owner=self.request.user) | Q(participants__student=self.request.user)
        ).distinct().prefetch_related('participants')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(owner=self.request.user).prefetch_related('participants')


class EventParticipantListCreateView(generics.ListCreateAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['event_id'], owner=self.request.user)

    def get_queryset(self):
        return Participant.objects.filter(event=self.get_event()).select_related('student')

    def perform_create(self, serializer):
        serializer.save(event=self.get_event())


class EventParticipantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Participant.objects.filter(
            event__pk=self.kwargs['event_id'], event__owner=self.request.user
        ).select_related('student')


# ============ COURSE VIEWS ============

class CourseListView(generics.ListCreateAPIView):
    """List all courses or create new"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_type', 'department', 'credits']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'credits', 'difficulty_rating']


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a course"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


# ============ CLASS SCHEDULE VIEWS ============

class ClassScheduleListView(generics.ListCreateAPIView):
    """List all class schedules or create new"""
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'day_of_week', 'session_type']


class ClassScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a class schedule"""
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
    permission_classes = [IsAuthenticated]


# ============ STUDENT ENROLLMENT VIEWS ============

class MyCoursesView(generics.ListAPIView):
    """List current student's enrolled courses"""
    serializer_class = StudentCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentCourse.objects.filter(
            student=self.request.user,
            semester='semester_2',
            academic_year='2026'
        )


class EnrollCourseView(generics.CreateAPIView):
    """Enroll in a course"""
    serializer_class = StudentCourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class UnenrollCourseView(generics.DestroyAPIView):
    """Unenroll from a course"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentCourse.objects.filter(student=self.request.user)


# ============ ASSIGNMENT VIEWS ============

class AssignmentListView(generics.ListCreateAPIView):
    """List assignments or create new"""
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'assessment_type', 'priority']
    ordering_fields = ['due_date', 'priority', 'weight_percentage']

    def get_queryset(self):
        # Get assignments for student's enrolled courses
        student_courses = StudentCourse.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)
        return Assignment.objects.filter(course_id__in=student_courses)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an assignment"""
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_courses = StudentCourse.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)
        return Assignment.objects.filter(course_id__in=student_courses)


class UpcomingAssignmentsView(generics.ListAPIView):
    """List upcoming assignments for current student"""
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_courses = StudentCourse.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)
        return Assignment.objects.filter(
            course_id__in=student_courses,
            due_date__gte=datetime.now()
        ).order_by('due_date')[:10]


# ============ EXAM SCHEDULE VIEWS ============

class ExamScheduleListView(generics.ListCreateAPIView):
    """List exam schedules"""
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_courses = StudentCourse.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)
        return ExamSchedule.objects.filter(course_id__in=student_courses)


# ============ CONFLICT DETECTION API ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detect_conflicts(request):
    """
    Detect scheduling conflicts for the current student
    Returns: overlapping classes, back-to-back exams, deadline clustering
    """
    student = request.user

    # Get student's class schedules
    student_courses = StudentCourse.objects.filter(student=student).values_list('course_id', flat=True)
    schedules = ClassSchedule.objects.all()
    exams = ExamSchedule.objects.filter(course_id__in=student_courses)
    assignments = Assignment.objects.filter(course_id__in=student_courses, due_date__gte=datetime.now())

    conflicts = {
        'overlapping_classes': [],
        'back_to_back_exams': [],
        'deadline_clustering': [],
        'total_conflicts': 0
    }

    # Detect overlapping classes
    schedule_list = list(schedules)
    for i in range(len(schedule_list)):
        for j in range(i + 1, len(schedule_list)):
            s1, s2 = schedule_list[i], schedule_list[j]
            if (s1.day_of_week == s2.day_of_week and
                s1.start_time < s2.end_time and
                s2.start_time < s1.end_time):
                conflicts['overlapping_classes'].append({
                    'class_1': ClassScheduleSerializer(s1).data,
                    'class_2': ClassScheduleSerializer(s2).data,
                    'conflict_type': 'overlap',
                    'severity': 'critical'
                })

    # Detect back-to-back exams (< 2 hours gap)
    exam_list = list(exams)
    for i in range(len(exam_list)):
        for j in range(i + 1, len(exam_list)):
            e1, e2 = exam_list[i], exam_list[j]
            if e1.date == e2.date:
                t1_end = datetime.combine(e1.date, e1.end_time)
                t2_start = datetime.combine(e2.date, e2.start_time)
                gap = (t2_start - t1_end).total_seconds() / 3600

                if 0 <= gap < 2:
                    conflicts['back_to_back_exams'].append({
                        'exam_1': ExamScheduleSerializer(e1).data,
                        'exam_2': ExamScheduleSerializer(e2).data,
                        'gap_hours': round(gap, 2),
                        'conflict_type': 'back_to_back',
                        'severity': 'warning'
                    })

    # Detect deadline clustering (3+ assignments within 3 days)
    assignment_list = list(assignments.order_by('due_date'))
    for i in range(len(assignment_list)):
        cluster = [assignment_list[i]]
        for j in range(i + 1, len(assignment_list)):
            diff = (assignment_list[j].due_date - assignment_list[i].due_date).days
            if diff <= 3:
                cluster.append(assignment_list[j])

        if len(cluster) >= 3:
            conflicts['deadline_clustering'].append({
                'assignments': AssignmentSerializer(cluster, many=True).data,
                'cluster_size': len(cluster),
                'date_range': f"{cluster[0].due_date.date()} to {cluster[-1].due_date.date()}",
                'conflict_type': 'deadline_cluster',
                'severity': 'warning'
            })

    conflicts['total_conflicts'] = (
        len(conflicts['overlapping_classes']) +
        len(conflicts['back_to_back_exams']) +
        len(conflicts['deadline_clustering'])
    )

    return Response(conflicts)


# ============ DASHBOARD SUMMARY API ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get dashboard summary for current student"""
    student = request.user

    student_courses = StudentCourse.objects.filter(student=student)
    course_ids = student_courses.values_list('course_id', flat=True)

    today = datetime.now()
    week_end = today + timedelta(days=7)

    data = {
        'total_courses': student_courses.count(),
        'total_credits': sum(sc.course.credits for sc in student_courses),
        'upcoming_classes_today': ClassSchedule.objects.filter(
            course_id__in=course_ids,
            day_of_week=today.weekday()
        ).count(),
        'assignments_this_week': Assignment.objects.filter(
            course_id__in=course_ids,
            due_date__range=[today, week_end]
        ).count(),
        'upcoming_exams': ExamSchedule.objects.filter(
            course_id__in=course_ids,
            date__gte=today.date()
        ).count(),
        'recent_conflicts': 0  # Would call detect_conflicts logic
    }

    return Response(data)
