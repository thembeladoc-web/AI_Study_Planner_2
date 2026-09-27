"""
Account Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

Student = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    """Student profile serializer"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'student_number', 'program', 'year_of_study', 'phone',
            'study_preference', 'max_study_hours_per_day', 'preferred_break_duration',
            'email_notifications', 'push_notifications', 'is_staff', 'is_superuser',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'created_at', 'updated_at']


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Registration serializer with password validation"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Student
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'student_number', 'program',
            'year_of_study', 'study_preference'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        student = Student.objects.create_user(**validated_data)
        return student


class StudentLoginSerializer(serializers.Serializer):
    """Login serializer"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
