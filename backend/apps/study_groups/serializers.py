"""
Study Groups Serializers
"""
from rest_framework import serializers
from .models import StudyGroup, GroupMembership, GroupMeeting, GroupMessage
from apps.timetable.serializers import CourseSerializer
from apps.timetable.models import Course
from apps.accounts.serializers import StudentSerializer


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Group membership serializer"""
    student = StudentSerializer(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = GroupMembership
        fields = [
            'id', 'group', 'student', 'student_name',
            'status', 'role', 'joined_at', 'left_at'
        ]


class StudyGroupSerializer(serializers.ModelSerializer):
    """Study group serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    current_member_count = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    members = GroupMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'description', 'course', 'course_id',
            'max_members', 'privacy', 'status',
            'preferred_day', 'preferred_time_start', 'preferred_time_end',
            'venue', 'is_online', 'meeting_link',
            'created_by', 'created_by_name',
            'current_member_count', 'available_slots', 'is_full',
            'members', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class GroupMeetingSerializer(serializers.ModelSerializer):
    """Group meeting serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = GroupMeeting
        fields = [
            'id', 'group', 'title', 'description',
            'date', 'start_time', 'end_time',
            'venue', 'is_online', 'meeting_link',
            'status', 'created_by', 'created_by_name', 'created_at'
        ]


class GroupMessageSerializer(serializers.ModelSerializer):
    """Group message serializer"""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = GroupMessage
        fields = [
            'id', 'group', 'sender', 'sender_name',
            'content', 'created_at', 'is_edited', 'edited_at'
        ]
        read_only_fields = ['sender']
