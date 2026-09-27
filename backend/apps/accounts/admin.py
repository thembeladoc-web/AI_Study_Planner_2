"""
Accounts Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'student_number', 'program', 'year_of_study', 'is_active']
    list_filter = ['year_of_study', 'program', 'is_active', 'study_preference']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Information', {
            'fields': ('student_number', 'program', 'year_of_study', 'phone')
        }),
        ('Study Preferences', {
            'fields': ('study_preference', 'max_study_hours_per_day', 'preferred_break_duration')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'push_notifications')
        }),
    )
