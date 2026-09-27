"""
Study Groups Admin Configuration
"""
from django.contrib import admin
from .models import StudyGroup, GroupMembership, GroupMeeting, GroupMessage


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'current_member_count', 'max_members', 'privacy', 'status']
    list_filter = ['privacy', 'status']
    search_fields = ['name', 'course__code']


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'student', 'status', 'role']
    list_filter = ['status', 'role']
    search_fields = ['group__name', 'student__username']


@admin.register(GroupMeeting)
class GroupMeetingAdmin(admin.ModelAdmin):
    list_display = ['group', 'title', 'date', 'start_time', 'status']
    list_filter = ['status']
    search_fields = ['title', 'group__name']
    date_hierarchy = 'date'


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ['group', 'sender', 'content', 'created_at']
    search_fields = ['content', 'group__name', 'sender__username']
