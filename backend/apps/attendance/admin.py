"""
Attendance Admin Configuration
"""
from django.contrib import admin
from .models import AttendanceRecord, AttendanceSummary


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_schedule', 'date', 'status', 'minutes_late']
    list_filter = ['status', 'date']
    search_fields = ['student__username', 'class_schedule__course__code']
    date_hierarchy = 'date'


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'attendance_percentage', 'is_below_minimum', 'warning_count']
    list_filter = ['course']
    search_fields = ['student__username', 'course__code']
