"""
Timetable Models - Courses, Classes, and Schedule Entries
"""
from django.db import models
from django.conf import settings


class Course(models.Model):
    """Academic course catalog"""

    COURSE_TYPE_CHOICES = [
        ('core', 'Core'),
        ('elective', 'Elective'),
        ('prerequisite', 'Prerequisite'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField(default=3)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='core')
    department = models.CharField(max_length=100, blank=True)
    lecturer_name = models.CharField(max_length=100, blank=True)
    lecturer_email = models.EmailField(blank=True)

    # Difficulty rating (1-5, used by AI scheduler)
    difficulty_rating = models.PositiveSmallIntegerField(default=3)
    estimated_study_hours_per_week = models.PositiveSmallIntegerField(default=6)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSchedule(models.Model):
    """Individual class session (lecture, tutorial, lab)"""

    SESSION_TYPE_CHOICES = [
        ('lecture', 'Lecture'),
        ('tutorial', 'Tutorial'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar'),
        ('workshop', 'Workshop'),
    ]

    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='lecture')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    building = models.CharField(max_length=100, blank=True)
    room_number = models.CharField(max_length=20, blank=True)

    # For recurring schedules
    is_recurring = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    # For one-off sessions
    specific_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'class_schedules'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        day_name = dict(self.DAY_CHOICES).get(self.day_of_week, 'Unknown')
        return f"{self.course.code} - {self.session_type} ({day_name} {self.start_time}-{self.end_time})"

    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        from datetime import datetime
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)


class StudentCourse(models.Model):
    """Many-to-many relationship between students and courses"""

    SEMESTER_CHOICES = [
        ('semester_1', 'Semester 1'),
        ('semester_2', 'Semester 2'),
        ('winter', 'Winter Term'),
        ('summer', 'Summer Term'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrolled_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, default='semester_2')
    academic_year = models.CharField(max_length=10, default='2026')
    enrollment_date = models.DateField(auto_now_add=True)

    # Student-specific overrides
    personal_difficulty_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    target_grade = models.CharField(max_length=5, blank=True)

    class Meta:
        db_table = 'student_courses'
        unique_together = ['student', 'course', 'semester', 'academic_year']

    def __str__(self):
        return f"{self.student.username} - {self.course.code} ({self.semester})"


class Assignment(models.Model):
    """Assignments, tests, and examinations"""

    ASSESSMENT_TYPE_CHOICES = [
        ('assignment', 'Assignment'),
        ('test', 'Test'),
        ('exam', 'Examination'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('presentation', 'Presentation'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES, default='assignment')
    due_date = models.DateTimeField()
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=2)

    # Estimated time to complete (hours)
    estimated_hours = models.PositiveSmallIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.course.code} - {self.title} (Due: {self.due_date.date()})"


class Event(models.Model):
    """A personal or academic calendar event owned by a student."""
    EVENT_TYPE_CHOICES = [
        ('class', 'Class'), ('study', 'Study'), ('exam', 'Exam'),
        ('assignment', 'Assignment'), ('meeting', 'Meeting'), ('other', 'Other'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['start_time']
        indexes = [models.Index(fields=['owner', 'start_time'])]
        constraints = [models.CheckConstraint(check=models.Q(end_time__gt=models.F('start_time')), name='event_end_after_start')]

    def __str__(self):
        return f"{self.title} ({self.start_time})"


class Participant(models.Model):
    """A person invited to or participating in an event."""
    STATUS_CHOICES = [
        ('invited', 'Invited'), ('accepted', 'Accepted'),
        ('declined', 'Declined'), ('tentative', 'Tentative'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_participations')
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'participants'
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['event', 'email'], name='unique_event_participant_email')]

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class ExamSchedule(models.Model):
    """Examination schedule entries"""

    EXAM_TYPE_CHOICES = [
        ('midterm', 'Mid-Term Examination'),
        ('final', 'Final Examination'),
        ('supplementary', 'Supplementary Examination'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='final')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=120)

    # For conflict detection
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = 'exam_schedules'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.course.code} - {self.exam_type} ({self.date})"
