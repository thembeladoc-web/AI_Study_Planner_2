"""
Study Groups URL Configuration
"""
from django.urls import path
from .views import (
    StudyGroupListView, StudyGroupDetailView,
    GroupMembershipListView, JoinGroupView, LeaveGroupView,
    GroupMeetingListView, GroupMeetingDetailView,
    GroupMessageListView,
    find_study_groups, my_groups_summary
)

urlpatterns = [
    path('groups/', StudyGroupListView.as_view(), name='study-group-list'),
    path('groups/<int:pk>/', StudyGroupDetailView.as_view(), name='study-group-detail'),
    path('groups/<int:group_id>/join/', JoinGroupView.as_view(), name='join-group'),
    path('groups/<int:group_id>/leave/', LeaveGroupView.as_view(), name='leave-group'),
    path('memberships/', GroupMembershipListView.as_view(), name='membership-list'),
    path('find/', find_study_groups, name='find-study-groups'),
    path('my-groups/', my_groups_summary, name='my-groups-summary'),
    path('meetings/', GroupMeetingListView.as_view(), name='meeting-list'),
    path('meetings/<int:pk>/', GroupMeetingDetailView.as_view(), name='meeting-detail'),
    path('messages/', GroupMessageListView.as_view(), name='message-list'),
]
