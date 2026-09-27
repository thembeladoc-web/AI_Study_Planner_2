"""
Account Views
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password

from .serializers import (
    StudentSerializer, 
    StudentRegistrationSerializer, 
    StudentLoginSerializer,
    PasswordChangeSerializer
)

Student = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Student registration endpoint"""
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        token, created = Token.objects.get_or_create(user=student)
        return Response({
            'user': StudentSerializer(student).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Student login endpoint"""
    serializer_class = StudentLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        student = authenticate(username=username, password=password)

        if student:
            token, created = Token.objects.get_or_create(user=student)
            return Response({
                'user': StudentSerializer(student).data,
                'token': token.key,
                'message': 'Login successful'
            })

        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(generics.GenericAPIView):
    """Student logout endpoint"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})


class ProfileView(generics.RetrieveUpdateAPIView):
    """Student profile endpoint"""
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """Password change endpoint"""
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = request.user
        if not check_password(serializer.validated_data['old_password'], student.password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student.set_password(serializer.validated_data['new_password'])
        student.save()

        # Delete old token and create new one
        Token.objects.filter(user=student).delete()
        token = Token.objects.create(user=student)

        return Response({
            'message': 'Password changed successfully',
            'token': token.key
        })
