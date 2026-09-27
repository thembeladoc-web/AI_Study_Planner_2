"""
Scheduler Views - AI Study Plan Generation using OR-Tools
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, time
from ortools.sat.python import cp_model
import json

from .models import StudyPlan, StudySession
from .serializers import StudyPlanSerializer, StudySessionSerializer
from apps.timetable.models import Course, ClassSchedule, StudentCourse, Assignment, ExamSchedule


class StudyPlanListView(generics.ListCreateAPIView):
    """List all study plans or create new"""
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudyPlan.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class StudyPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a study plan"""
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudyPlan.objects.filter(student=self.request.user)


class StudySessionListView(generics.ListCreateAPIView):
    """List study sessions or create new"""
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(study_plan__student=self.request.user)


class StudySessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a study session"""
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(study_plan__student=self.request.user)


# ============ AI STUDY PLAN GENERATOR ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_study_plan(request):
    """
    Generate an optimized study plan using Google OR-Tools CP-SAT solver

    Request body:
    {
        "week_start": "2026-06-01",
        "week_end": "2026-06-07",
        "courses": [1, 2, 3],  // optional, defaults to enrolled courses
        "preferences": {
            "max_hours_per_day": 6,
            "preferred_times": ["morning", "afternoon"],
            "min_break_minutes": 30
        }
    }
    """
    import time as time_module
    start_time = time_module.time()

    student = request.user
    data = request.data

    week_start = datetime.strptime(data.get('week_start'), '%Y-%m-%d').date()
    week_end = datetime.strptime(data.get('week_end'), '%Y-%m-%d').date()

    # Get student's courses
    if 'courses' in data:
        course_ids = data['courses']
    else:
        course_ids = StudentCourse.objects.filter(
            student=student,
            semester='semester_2',
            academic_year='2026'
        ).values_list('course_id', flat=True)

    courses = Course.objects.filter(id__in=course_ids)

    if not courses.exists():
        return Response(
            {'error': 'No courses found. Please enroll in courses first.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get preferences
    prefs = data.get('preferences', {})
    max_hours_per_day = prefs.get('max_hours_per_day', student.max_study_hours_per_day or 6)
    min_break = prefs.get('min_break_minutes', student.preferred_break_duration or 30)
    study_preference = student.study_preference or 'flexible'

    # Get existing class schedules for the week
    existing_schedules = ClassSchedule.objects.filter(
        course_id__in=course_ids,
        is_recurring=True
    )

    # Get upcoming assignments
    assignments = Assignment.objects.filter(
        course_id__in=course_ids,
        due_date__gte=datetime.combine(week_start, time.min),
        due_date__lte=datetime.combine(week_end, time.max)
    )

    # ============ OR-TOOLS CONSTRAINT SOLVER ============
    model = cp_model.CpModel()

    # Define time slots: 30-minute blocks from 6:00 to 23:00
    SLOT_DURATION = 30  # minutes
    START_HOUR = 6
    END_HOUR = 23
    SLOTS_PER_DAY = (END_HOUR - START_HOUR) * 2  # 34 slots per day
    DAYS = 7  # Monday to Sunday

    # Create decision variables: x[course][day][slot] = 0 or 1
    study_slots = {}
    for course in courses:
        for day in range(DAYS):
            for slot in range(SLOTS_PER_DAY):
                study_slots[(course.id, day, slot)] = model.NewBoolVar(
                    f'study_c{course.id}_d{day}_s{slot}'
                )

    # ============ HARD CONSTRAINTS ============

    # 1. No overlap with existing classes
    for schedule in existing_schedules:
        day = schedule.day_of_week
        start_slot = (schedule.start_time.hour - START_HOUR) * 2 + schedule.start_time.minute // 30
        end_slot = (schedule.end_time.hour - START_HOUR) * 2 + schedule.end_time.minute // 30

        for course in courses:
            for slot in range(max(0, start_slot), min(SLOTS_PER_DAY, end_slot)):
                model.Add(study_slots[(course.id, day, slot)] == 0)

    # 2. Maximum hours per day
    for day in range(DAYS):
        daily_slots = []
        for course in courses:
            for slot in range(SLOTS_PER_DAY):
                daily_slots.append(study_slots[(course.id, day, slot)])
        model.Add(sum(daily_slots) <= max_hours_per_day * 2)  # *2 because slots are 30 min

    # 3. Minimum break between study sessions (30 min = 1 slot)
    for course in courses:
        for day in range(DAYS):
            for slot in range(SLOTS_PER_DAY - 1):
                # If studying at slot, can't study at slot+1 (break requirement)
                # Relaxed: allow consecutive if same course
                pass  # Simplified for this version

    # 4. Each course gets minimum study time based on credits and difficulty
    for course in courses:
        min_slots = course.credits * 2  # 1 hour per credit per week minimum
        course_slots = []
        for day in range(DAYS):
            for slot in range(SLOTS_PER_DAY):
                course_slots.append(study_slots[(course.id, day, slot)])
        model.Add(sum(course_slots) >= min_slots)

    # ============ SOFT CONSTRAINTS / OBJECTIVE ============

    # Objective: Maximize study quality score
    # Score = difficulty_weight * preference_alignment * deadline_proximity
    objective_terms = []

    for course in courses:
        difficulty = course.difficulty_rating or 3

        for day in range(DAYS):
            for slot in range(SLOTS_PER_DAY):
                # Time preference score
                hour = START_HOUR + slot // 2
                preference_score = get_preference_score(hour, study_preference)

                # Deadline proximity score (higher if assignment due soon)
                deadline_score = get_deadline_score(course, assignments, day)

                # Combined score
                score = int(difficulty * preference_score * deadline_score * 10)
                objective_terms.append(score * study_slots[(course.id, day, slot)])

    model.Maximize(sum(objective_terms))

    # ============ SOLVE ============
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0  # Max 5 seconds
    solver.parameters.num_search_workers = 4

    result = solver.Solve(model)

    if result not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return Response(
            {'error': 'Could not generate a feasible study plan. Try relaxing constraints.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ============ CREATE STUDY PLAN ============
    study_plan = StudyPlan.objects.create(
        student=student,
        name=f"Study Plan: {week_start} to {week_end}",
        week_start=week_start,
        week_end=week_end,
        status='active',
        generation_time_ms=int((time_module.time() - start_time) * 1000),
        optimization_score=round(solver.ObjectiveValue() / 100, 2) if result == cp_model.OPTIMAL else None
    )

    # Extract solution and create study sessions
    sessions_created = []
    for course in courses:
        for day in range(DAYS):
            slots = []
            for slot in range(SLOTS_PER_DAY):
                if solver.Value(study_slots[(course.id, day, slot)]) == 1:
                    slots.append(slot)

            # Group consecutive slots into sessions
            if slots:
                sessions = group_consecutive_slots(slots)
                for session_slots in sessions:
                    start_slot = session_slots[0]
                    end_slot = session_slots[-1] + 1

                    start_time_obj = time(
                        START_HOUR + start_slot // 2,
                        (start_slot % 2) * 30
                    )
                    end_time_obj = time(
                        START_HOUR + end_slot // 2,
                        (end_slot % 2) * 30
                    )

                    duration = (end_slot - start_slot) * 30

                    # Determine session type based on course and timing
                    session_type = determine_session_type(course, duration)

                    study_session = StudySession.objects.create(
                        study_plan=study_plan,
                        course=course,
                        day_of_week=day,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        duration_minutes=duration,
                        session_type=session_type,
                        topic=f"Study {course.code}",
                        priority_score=round(difficulty * preference_score / 10, 2),
                        difficulty_weight=course.difficulty_rating
                    )
                    sessions_created.append(study_session)

    return Response({
        'study_plan': StudyPlanSerializer(study_plan).data,
        'sessions_created': len(sessions_created),
        'solver_status': 'OPTIMAL' if result == cp_model.OPTIMAL else 'FEASIBLE',
        'generation_time_ms': study_plan.generation_time_ms,
        'message': 'Study plan generated successfully'
    })


def get_preference_score(hour, preference):
    """Return preference score (1-5) based on time of day and student preference"""
    scores = {
        'morning': {6: 5, 7: 5, 8: 5, 9: 4, 10: 4, 11: 3, 12: 2, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1},
        'afternoon': {6: 1, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 5, 13: 5, 14: 4, 15: 4, 16: 3, 17: 2, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1},
        'evening': {6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 2, 14: 2, 15: 3, 16: 4, 17: 5, 18: 5, 19: 5, 20: 4, 21: 4, 22: 3},
        'night': {6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 2, 20: 3, 21: 4, 22: 5},
        'flexible': {h: 3 for h in range(6, 23)},
    }
    return scores.get(preference, scores['flexible']).get(hour, 1)


def get_deadline_score(course, assignments, day_offset):
    """Higher score if assignment due soon"""
    from datetime import timedelta
    target_date = datetime.now().date() + timedelta(days=day_offset)

    course_assignments = [a for a in assignments if a.course_id == course.id]
    if not course_assignments:
        return 1.0

    # Find closest assignment
    closest_days = min(
        [(a.due_date.date() - target_date).days for a in course_assignments],
        default=999
    )

    if closest_days <= 0:
        return 5.0  # Due today or overdue
    elif closest_days <= 2:
        return 4.0
    elif closest_days <= 5:
        return 3.0
    elif closest_days <= 10:
        return 2.0
    else:
        return 1.0


def group_consecutive_slots(slots):
    """Group consecutive slot numbers into sessions"""
    if not slots:
        return []

    sessions = []
    current = [slots[0]]

    for slot in slots[1:]:
        if slot == current[-1] + 1:
            current.append(slot)
        else:
            sessions.append(current)
            current = [slot]
    sessions.append(current)

    return sessions


def determine_session_type(course, duration_minutes):
    """Determine session type based on course and duration"""
    if duration_minutes <= 30:
        return 'review'
    elif duration_minutes <= 60:
        return 'reading'
    elif course.code.startswith('MAT') or course.code.startswith('PHY'):
        return 'practice'
    else:
        return 'deep_study'


# ============ STUDY PLAN UTILITIES ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_session_complete(request, session_id):
    """Mark a study session as completed"""
    session = get_object_or_404(
        StudySession,
        id=session_id,
        study_plan__student=request.user
    )

    session.is_completed = True
    session.actual_duration_minutes = request.data.get('actual_duration_minutes', session.duration_minutes)
    session.completion_notes = request.data.get('notes', '')
    session.completed_at = datetime.now()
    session.save()

    return Response({
        'message': 'Session marked as complete',
        'session': StudySessionSerializer(session).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def study_plan_stats(request, plan_id):
    """Get statistics for a study plan"""
    plan = get_object_or_404(StudyPlan, id=plan_id, student=request.user)
    sessions = plan.sessions.all()

    total_sessions = sessions.count()
    completed_sessions = sessions.filter(is_completed=True).count()
    total_planned_minutes = sum(s.duration_minutes for s in sessions)
    total_actual_minutes = sum(s.actual_duration_minutes or 0 for s in sessions)

    # Per-course breakdown
    course_stats = {}
    for session in sessions:
        code = session.course.code
        if code not in course_stats:
            course_stats[code] = {
                'course_name': session.course.name,
                'total_sessions': 0,
                'completed_sessions': 0,
                'planned_minutes': 0,
                'actual_minutes': 0
            }
        course_stats[code]['total_sessions'] += 1
        course_stats[code]['planned_minutes'] += session.duration_minutes
        if session.is_completed:
            course_stats[code]['completed_sessions'] += 1
            course_stats[code]['actual_minutes'] += session.actual_duration_minutes or 0

    return Response({
        'plan_name': plan.name,
        'completion_rate': round(completed_sessions / total_sessions * 100, 2) if total_sessions else 0,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_planned_hours': round(total_planned_minutes / 60, 2),
        'total_actual_hours': round(total_actual_minutes / 60, 2),
        'adherence_rate': round(total_actual_minutes / total_planned_minutes * 100, 2) if total_planned_minutes else 0,
        'course_breakdown': course_stats
    })
