from django.conf import settings
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'app_id', 'email', 'mobile', 'name', 'dob',
                'gender', 'country', 'genres_selected', 'created_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    genres_selected = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,  # Ensures at least one genre is selected
        max_length=10  # Limits selection to 10 genres
    )

    class Meta:
        model = User
        fields = ["email", "mobile", "name", "dob", "gender", "country", "genres_selected", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_genres_selected(self, value):
        """Ensure genres are valid and do not exceed the limit"""
        available_genres = getattr(settings, "AVAILABLE_GENRES", [])
        invalid_genres = [genre for genre in value if genre not in available_genres]

        if invalid_genres:
            raise serializers.ValidationError(f"Invalid genres selected: {invalid_genres}")

        if len(value) > 10:
            raise serializers.ValidationError("You can select a maximum of 10 genres.")

        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "country", "genres_selected", 
                "mobile", "gender", "dob"]
        extra_kwargs = {
            "mobile": {"required": False},
            "dob": {"required": False},
            "gender": {"required": False}
        }

