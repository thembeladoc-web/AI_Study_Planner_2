"""
Scheduler Models - Study Plans and Sessions
"""
from django.db import models
from django.conf import settings


class StudyPlan(models.Model):
    """Generated study plan for a student"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('draft', 'Draft'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_plans')
    name = models.CharField(max_length=200, default='My Study Plan')
    week_start = models.DateField()
    week_end = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # AI generation metadata
    generation_time_ms = models.PositiveIntegerField(null=True, blank=True)
    optimization_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.name} ({self.week_start} to {self.week_end})"


class StudySession(models.Model):
    """Individual study session within a plan"""

    SESSION_TYPE_CHOICES = [
        ('review', 'Review'),
        ('deep_study', 'Deep Study'),
        ('practice', 'Practice Problems'),
        ('reading', 'Reading'),
        ('memorization', 'Memorization'),
        ('group_study', 'Group Study'),
    ]

    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='sessions')
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE, related_name='study_sessions')

    day_of_week = models.PositiveSmallIntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField()

    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='deep_study')
    topic = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    # AI scoring
    priority_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    difficulty_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)

    # Completion tracking
    is_completed = models.BooleanField(default=False)
    actual_duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_sessions'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.course.code} - {self.session_type} ({self.get_day_of_week_display()} {self.start_time})"
