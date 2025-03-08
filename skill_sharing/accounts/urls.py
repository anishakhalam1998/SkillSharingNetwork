from django.urls import path
from .views import UserProfileView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),  # ✅ This should match frontend URL
]
