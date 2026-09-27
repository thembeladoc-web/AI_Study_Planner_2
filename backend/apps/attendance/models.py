"""
Attendance Models
"""
from django.db import models
from django.conf import settings


class AttendanceRecord(models.Model):
    """Individual attendance record for a class session"""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
        ('cancelled', 'Class Cancelled'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    class_schedule = models.ForeignKey('timetable.ClassSchedule', on_delete=models.CASCADE, related_name='attendance_records')

    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    # For late arrivals
    minutes_late = models.PositiveSmallIntegerField(default=0)

    # Notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_records'
        unique_together = ['student', 'class_schedule', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.class_schedule.course.code} ({self.date}: {self.status})"


class AttendanceSummary(models.Model):
    """Rolling attendance summary per course per student"""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_summaries')
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE, related_name='attendance_summaries')

    total_sessions = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)

    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)

    # Thresholds
    minimum_required_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=80.00)
    warning_threshold_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=85.00)

    # Alert tracking
    last_warning_sent = models.DateTimeField(null=True, blank=True)
    warning_count = models.PositiveSmallIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_summaries'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.code}: {self.attendance_percentage}%"

    def calculate_percentage(self):
        """Recalculate attendance percentage"""
        countable = self.total_sessions - self.excused_count
        if countable == 0:
            self.attendance_percentage = 100.00
        else:
            self.attendance_percentage = round(
                (self.present_count + self.late_count) / countable * 100, 2
            )
        return self.attendance_percentage

    @property
    def sessions_needed_for_minimum(self):
        """Return the additional attended sessions needed to reach the minimum."""
        if self.attendance_percentage >= self.minimum_required_percentage:
            return 0
        countable = self.total_sessions - self.excused_count
        attended = self.present_count + self.late_count
        needed = 0
        while countable + needed > 0 and (attended + needed) / (countable + needed) * 100 < float(self.minimum_required_percentage):
            needed += 1
        return needed

    @property
    def is_below_minimum(self):
        return self.attendance_percentage < self.minimum_required_percentage

    @property
    def is_near_threshold(self):
        return self.attendance_percentage < self.warning_threshold_percentage
