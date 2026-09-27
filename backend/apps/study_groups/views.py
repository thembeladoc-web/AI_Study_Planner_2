"""
Study Groups Views - Group Study Matching
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import StudyGroup, GroupMembership, GroupMeeting, GroupMessage
from .serializers import (
    StudyGroupSerializer, GroupMembershipSerializer,
    GroupMeetingSerializer, GroupMessageSerializer
)
from apps.timetable.models import StudentCourse, ClassSchedule


class StudyGroupListView(generics.ListCreateAPIView):
    """List all study groups or create new"""
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StudyGroup.objects.filter(status='active')

        # Filter by course if provided
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # Filter by privacy
        privacy = self.request.query_params.get('privacy')
        if privacy:
            queryset = queryset.filter(privacy=privacy)

        # Filter by day
        day = self.request.query_params.get('day')
        if day:
            queryset = queryset.filter(preferred_day=day)

        return queryset

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        # Creator automatically becomes admin
        GroupMembership.objects.create(
            group=group,
            student=self.request.user,
            status='active',
            role='admin'
        )


class StudyGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a study group"""
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudyGroup.objects.all()


class GroupMembershipListView(generics.ListCreateAPIView):
    """List or create group memberships"""
    serializer_class = GroupMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupMembership.objects.filter(student=self.request.user)


class JoinGroupView(generics.CreateAPIView):
    """Request to join a study group"""
    serializer_class = GroupMembershipSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(StudyGroup, id=group_id)
        student = request.user

        # Check if already a member
        if GroupMembership.objects.filter(group=group, student=student).exists():
            return Response(
                {'error': 'You are already a member of this group'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if group is full
        if group.is_full:
            return Response(
                {'error': 'This group is full'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if student is enrolled in the course
        if not StudentCourse.objects.filter(student=student, course=group.course).exists():
            return Response(
                {'error': 'You must be enrolled in this course to join the study group'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Determine membership status based on privacy
        membership_status = 'active' if group.privacy == 'public' else 'pending'

        membership = GroupMembership.objects.create(
            group=group,
            student=student,
            status=membership_status,
            role='member'
        )

        # Update group status if now full
        if group.is_full:
            group.status = 'full'
            group.save()

        return Response({
            'message': 'Join request submitted' if membership_status == 'pending' else 'Successfully joined group',
            'membership': GroupMembershipSerializer(membership).data
        })


class LeaveGroupView(generics.DestroyAPIView):
    """Leave a study group"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, group_id):
        group = get_object_or_404(StudyGroup, id=group_id)
        membership = get_object_or_404(
            GroupMembership,
            group=group,
            student=request.user,
            status='active'
        )

        membership.status = 'left'
        membership.left_at = datetime.now()
        membership.save()

        # Update group status if was full
        if group.status == 'full':
            group.status = 'active'
            group.save()

        return Response({'message': 'Successfully left the group'})


# ============ GROUP STUDY MATCHING ALGORITHM ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_study_groups(request):
    """
    Find recommended study groups for current student
    Uses compatibility scoring based on:
    - Shared courses
    - Temporal overlap in free time
    - Group size preference
    """
    student = request.user

    # Get student's enrolled courses
    enrolled_courses = StudentCourse.objects.filter(student=student).values_list('course_id', flat=True)

    # Get student's class schedules (busy times)
    busy_slots = get_student_busy_slots(student)

    # Find active groups for enrolled courses
    groups = StudyGroup.objects.filter(
        course_id__in=enrolled_courses,
        status='active',
        privacy__in=['public', 'invite_only']
    ).exclude(
        members__student=student  # Exclude groups already joined
    )

    # Score each group
    scored_groups = []
    for group in groups:
        score = calculate_group_compatibility(student, group, busy_slots)
        scored_groups.append({
            'group': StudyGroupSerializer(group).data,
            'compatibility_score': score,
            'reasons': get_compatibility_reasons(student, group, busy_slots)
        })

    # Sort by compatibility score (highest first)
    scored_groups.sort(key=lambda x: x['compatibility_score'], reverse=True)

    return Response({
        'recommended_groups': scored_groups[:10],
        'total_available': len(scored_groups)
    })


def get_student_busy_slots(student):
    """Get student's busy time slots for the week"""
    from collections import defaultdict

    busy = defaultdict(list)
    schedules = ClassSchedule.objects.filter(
        course__enrolled_students__student=student
    )

    for schedule in schedules:
        busy[schedule.day_of_week].append({
            'start': schedule.start_time,
            'end': schedule.end_time
        })

    return busy


def calculate_group_compatibility(student, group, busy_slots):
    """Calculate compatibility score (0-100)"""
    score = 0

    # Base score for shared course
    score += 30

    # Temporal compatibility (40 points max)
    if group.preferred_day is not None and group.preferred_time_start and group.preferred_time_end:
        day_busy = busy_slots.get(group.preferred_day, [])

        # Check if group time conflicts with classes
        has_conflict = False
        for slot in day_busy:
            if (slot['start'] < group.preferred_time_end and
                slot['end'] > group.preferred_time_start):
                has_conflict = True
                break

        if not has_conflict:
            score += 40
        else:
            # Partial score if only minor overlap
            score += 10
    else:
        # No preference set = flexible = good
        score += 25

    # Group size preference (20 points max)
    if group.current_member_count < 3:
        score += 20  # Small group, more intimate
    elif group.current_member_count < group.max_members - 1:
        score += 15  # Medium group
    else:
        score += 5   # Almost full

    # Online preference (10 points)
    if group.is_online:
        score += 10  # Online = more accessible

    return min(score, 100)


def get_compatibility_reasons(student, group, busy_slots):
    """Generate human-readable reasons for compatibility"""
    reasons = []

    reasons.append(f"You are enrolled in {group.course.code}")

    if group.preferred_day is not None:
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][group.preferred_day]

        day_busy = busy_slots.get(group.preferred_day, [])
        has_conflict = False
        for slot in day_busy:
            if (slot['start'] < group.preferred_time_end and
                slot['end'] > group.preferred_time_start):
                has_conflict = True
                break

        if not has_conflict:
            reasons.append(f"Meets on {day_name} when you are free")
        else:
            reasons.append(f"Meets on {day_name} (some schedule overlap)")

    if group.is_online:
        reasons.append("Online meeting - no travel needed")

    if group.current_member_count < 3:
        reasons.append("Small group - more focused discussion")

    return reasons


# ============ GROUP MEETING VIEWS ============

class GroupMeetingListView(generics.ListCreateAPIView):
    """List or create group meetings"""
    serializer_class = GroupMeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get meetings for groups the student is a member of
        member_groups = GroupMembership.objects.filter(
            student=self.request.user,
            status='active'
        ).values_list('group_id', flat=True)

        return GroupMeeting.objects.filter(group_id__in=member_groups)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GroupMeetingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a group meeting"""
    serializer_class = GroupMeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        member_groups = GroupMembership.objects.filter(
            student=self.request.user,
            status='active'
        ).values_list('group_id', flat=True)
        return GroupMeeting.objects.filter(group_id__in=member_groups)


# ============ GROUP MESSAGE VIEWS ============

class GroupMessageListView(generics.ListCreateAPIView):
    """List or create group messages"""
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.request.query_params.get('group')
        if group_id:
            # Check membership
            if not GroupMembership.objects.filter(
                group_id=group_id,
                student=self.request.user,
                status='active'
            ).exists():
                return GroupMessage.objects.none()
            return GroupMessage.objects.filter(group_id=group_id)
        return GroupMessage.objects.none()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


# ============ MY GROUPS SUMMARY ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_groups_summary(request):
    """Get summary of all groups the student is part of"""
    student = request.user

    memberships = GroupMembership.objects.filter(
        student=student,
        status='active'
    ).select_related('group', 'group__course')

    groups_data = []
    for membership in memberships:
        group = membership.group
        upcoming_meetings = GroupMeeting.objects.filter(
            group=group,
            date__gte=datetime.now().date(),
            status='scheduled'
        ).order_by('date', 'start_time')[:3]

        groups_data.append({
            'group': StudyGroupSerializer(group).data,
            'my_role': membership.role,
            'joined_at': membership.joined_at,
            'upcoming_meetings': GroupMeetingSerializer(upcoming_meetings, many=True).data
        })

    return Response({
        'total_groups': len(groups_data),
        'admin_groups': len([g for g in groups_data if g['my_role'] == 'admin']),
        'groups': groups_data
    })
