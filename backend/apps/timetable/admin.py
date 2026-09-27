"""
Timetable Admin Configuration
"""
from django.contrib import admin
from .models import Course, ClassSchedule, StudentCourse, Assignment, ExamSchedule, Event, Participant


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'event_type', 'start_time', 'end_time', 'location']
    list_filter = ['event_type', 'all_day']
    search_fields = ['title', 'description', 'location', 'owner__username']
    date_hierarchy = 'start_time'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'event', 'status', 'student']
    list_filter = ['status']
    search_fields = ['name', 'email', 'event__title', 'student__username']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'course_type', 'difficulty_rating', 'lecturer_name']
    list_filter = ['course_type', 'department', 'credits']
    search_fields = ['code', 'name', 'lecturer_name']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'session_type', 'day_of_week', 'start_time', 'end_time', 'venue']
    list_filter = ['day_of_week', 'session_type']
    search_fields = ['course__code', 'venue']


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'academic_year']
    list_filter = ['semester', 'academic_year']
    search_fields = ['student__username', 'course__code']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'assessment_type', 'due_date', 'weight_percentage', 'priority']
    list_filter = ['assessment_type', 'priority']
    search_fields = ['title', 'course__code']
    date_hierarchy = 'due_date'


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'exam_type', 'date', 'start_time', 'end_time', 'venue']
    list_filter = ['exam_type']
    search_fields = ['course__code', 'venue']
    date_hierarchy = 'date'
