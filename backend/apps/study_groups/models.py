"""
Study Groups Models
"""
from django.db import models
from django.conf import settings


class StudyGroup(models.Model):
    """Study group for collaborative learning"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('full', 'Full'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ]

    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('invite_only', 'Invite Only'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE, related_name='study_groups')

    # Group settings
    max_members = models.PositiveSmallIntegerField(default=5)
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Meeting preferences
    preferred_day = models.PositiveSmallIntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ], null=True, blank=True)
    preferred_time_start = models.TimeField(null=True, blank=True)
    preferred_time_end = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)

    # Creator
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_groups'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.course.code})"

    @property
    def current_member_count(self):
        return self.members.filter(status='active').count()

    @property
    def is_full(self):
        return self.current_member_count >= self.max_members

    @property
    def available_slots(self):
        return self.max_members - self.current_member_count


class GroupMembership(models.Model):
    """Membership in a study group"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('left', 'Left'),
        ('removed', 'Removed'),
    ]

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]

    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'group_memberships'
        unique_together = ['group', 'student']

    def __str__(self):
        return f"{self.student.username} in {self.group.name}"


class GroupMeeting(models.Model):
    """Scheduled study group meeting"""

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_meetings'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.group.name} - {self.title} ({self.date})"


class GroupMessage(models.Model):
    """Messages within a study group"""

    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'group_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
