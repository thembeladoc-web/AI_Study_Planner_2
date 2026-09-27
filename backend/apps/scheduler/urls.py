"""
Scheduler URL Configuration
"""
from django.urls import path
from .views import (
    StudyPlanListView, StudyPlanDetailView,
    StudySessionListView, StudySessionDetailView,
    generate_study_plan, mark_session_complete, study_plan_stats
)

urlpatterns = [
    path('plans/', StudyPlanListView.as_view(), name='study-plan-list'),
    path('plans/<int:pk>/', StudyPlanDetailView.as_view(), name='study-plan-detail'),
    path('sessions/', StudySessionListView.as_view(), name='study-session-list'),
    path('sessions/<int:pk>/', StudySessionDetailView.as_view(), name='study-session-detail'),
    path('generate/', generate_study_plan, name='generate-study-plan'),
    path('sessions/<int:session_id>/complete/', mark_session_complete, name='mark-complete'),
    path('plans/<int:plan_id>/stats/', study_plan_stats, name='study-plan-stats'),
]
