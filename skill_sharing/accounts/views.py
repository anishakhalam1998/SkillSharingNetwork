from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer

# User Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# Get Authenticated User Data
@api_view(['GET'])
def get_user(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

# ✅ Modified UserProfileView to Handle `PUT` Requests
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response({
            "user": {
                "username": request.user.username,
                "email": request.user.email
            },
            "mobile": profile.mobile,
            "skills_have": profile.skills_have,
            "skills_learn": profile.skills_learn
        })

    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update profile data with provided fields
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SkillMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            skills_to_learn = set(map(str.lower, user_profile.skills_learn or []))

            all_profiles = UserProfile.objects.exclude(user=request.user)
            matched_users = []

            for profile in all_profiles:
                skills_have_lower = set(map(str.lower, profile.skills_have or []))
                matched_skills = skills_to_learn.intersection(skills_have_lower)

                if matched_skills:
                    matched_users.append({
                        "username": profile.user.username,
                        "email": profile.user.email,
                        "matched_skills": list(matched_skills),
                        # ✅ Fix Profile Image Error (Only include if exists)
                        "profile_image": request.build_absolute_uri(profile.profile_image.url) if profile.profile_image else None,
                    })

            return Response({"matched_users": matched_users}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

