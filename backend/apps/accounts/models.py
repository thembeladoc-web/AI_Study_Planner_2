"""
Student User Model
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Student(AbstractUser):
    """Custom user model for students"""

    STUDY_PREFERENCE_CHOICES = [
        ('morning', 'Morning (6AM - 12PM)'),
        ('afternoon', 'Afternoon (12PM - 6PM)'),
        ('evening', 'Evening (6PM - 12AM)'),
        ('night', 'Night (12AM - 6AM)'),
        ('flexible', 'Flexible'),
    ]

    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    student_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    program = models.CharField(max_length=100, blank=True)
    year_of_study = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=1)
    phone = models.CharField(max_length=20, blank=True)

    # Study preferences for AI scheduling
    study_preference = models.CharField(
        max_length=20, 
        choices=STUDY_PREFERENCE_CHOICES, 
        default='flexible'
    )
    max_study_hours_per_day = models.PositiveSmallIntegerField(default=6)
    preferred_break_duration = models.PositiveSmallIntegerField(default=30)  # minutes

    # Notification settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_number or self.username})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
