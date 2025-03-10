from django.urls import path
from .views import UserProfileView, SkillMatchView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('skill-matching/', SkillMatchView.as_view(), name="skill-matching"),# ✅ This should match frontend URL
]
