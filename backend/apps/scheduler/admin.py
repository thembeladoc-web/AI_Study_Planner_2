"""
Scheduler Admin Configuration
"""
from django.contrib import admin
from .models import StudyPlan, StudySession


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ['student', 'name', 'week_start', 'week_end', 'status', 'optimization_score']
    list_filter = ['status', 'week_start']
    search_fields = ['student__username', 'name']
    date_hierarchy = 'week_start'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['study_plan', 'course', 'day_of_week', 'start_time', 'end_time', 'session_type', 'is_completed']
    list_filter = ['day_of_week', 'session_type', 'is_completed']
    search_fields = ['course__code', 'topic']
