from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserRegisterSerializer, UserSerializer ,UserUpdateSerializer
from django.contrib.auth import authenticate
from .tasks import send_otp, verify_otp
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
import random
from .services import  OtpService , JwtService
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
import uuid
from django.contrib.auth import get_user_model



class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        """Handles user registration & OTP verification."""
        data = request.data
        mobile = data.get("mobile")
        otp = data.get("otp")

        if not mobile:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: If no OTP is provided, send one (but only if the number is not already registered)
        if not otp:
            if User.objects.filter(mobile=mobile).exists():
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP and send to mobile
            otp = OtpService.generate_otp(mobile)  # Generate OTP (Make sure OTP service sends the OTP correctly)
            # You can log the OTP for debugging purposes (but avoid doing this in production)
            print(f"OTP sent to {mobile}: {otp}")  # Remove in production!

            return Response({"message": f"OTP sent to {mobile}"}, status=status.HTTP_200_OK)

        # Step 2: Verify OTP before proceeding to user registration
        if not OtpService.verify_otp(mobile, otp):
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate the other fields (like email, name, etc.)
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Create the user only after OTP verification and validation
        try:
            user = serializer.save()  # This will create the user using the UserRegisterSerializer

            # Generate JWT
            jwt_token = JwtService.create_jwt(user)  # Pass the user object, not just UUID

            return Response({
                "message": "User registered and login successful",
                "jwt": jwt_token,
                "user_details": {
                    "uuid": user.uuid,
                    "email": user.email,
                    "mobile": user.mobile,
                    "genres":user.genres_selected,
                    "name": user.name,
                }
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Email is not registered. Please sign up first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            refresh.payload["user_id"] = str(user.uuid)  # 👈 Ensure UUID is used

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": str(user.uuid),  # 👈 Return user UUID instead of id
            })
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class GetUserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user.refresh_from_db()  # Ensure latest data is fetched
        return user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()  # Fetch directly from DB
        response_data = {
            "uuid": str(user.uuid),
            "name": user.name,
            "email": user.email,
            "genres_selected": user.genres_selected if isinstance(user.genres_selected, list) else [],
            "country": user.country,  
            "mobile": user.mobile,
            "gender": {
                "Male": "Male",
                "Female": "Female",
                "Other": "Others"
            }.get(user.gender, "Not Specified"),
            "dob": user.dob.isoformat() if user.dob else None,
            "is_guest": getattr(user, "is_guest", False),  
            "is_verified": "Verified" if getattr(user, "is_verified", False) else "Not Verified",
            "status": {
                0: "Enabled",
                1: "Disabled",
                2: "Deleted"
            }.get(getattr(user, "status", 0), "Unknown"),
        }

        # Prevent frontend caching old data
        response = Response(response_data, status=status.HTTP_200_OK)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        
        return response



class UpdateProfileView(generics.UpdateAPIView):
    
  #  Update user profile details.
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    # Delete user account permanently.
  
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




class GenreSelectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return a list of available genres & user's selected genres."""
        return Response({
            "available_genres": AVAILABLE_GENRES,
            "selected_genres": request.user.genres_selected  # Fetch user-selected genres
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Fetch genres (if no body) OR Update selected genres if data is provided."""
        user = request.user
        selected_genres = request.data.get("genres_selected", [])

        # If no genres are provided, return available genres
        if not selected_genres:
            return Response({
                "available_genres": AVAILABLE_GENRES,
                "selected_genres": user.genres_selected
            }, status=status.HTTP_200_OK)

        # Validate genres
        if not isinstance(selected_genres, list):
            return Response({"error": "Genres must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)

        if len(selected_genres) > 10:
            return Response({"error": "You can select up to 10 genres only."}, status=status.HTTP_400_BAD_REQUEST)

        invalid_genres = [genre for genre in selected_genres if genre not in AVAILABLE_GENRES]
        if invalid_genres:
            return Response({"error": f"Invalid genres selected: {invalid_genres}"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the genres
        user.genres_selected = selected_genres
        user.save()

        return Response({
            "message": "Genres updated successfully",
            "selected_genres": user.genres_selected
        }, status=status.HTTP_200_OK)
