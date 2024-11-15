from rest_framework.viewsets import ViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from shared.utils import standard_response as Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken


class UserAuthViewSet(ViewSet):
    """
    ViewSet for managing user authentication and profiles.
    """

    @swagger_auto_schema(
        request_body=UserSignupSerializer,
        responses={201: UserSignupSerializer},
        operation_summary="User Signup",
        operation_description="Create a new user."
    )
    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            message="User created successfully.",
            status_code=status.HTTP_201_CREATED,
            data=serializer.data
        )

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                    },
                )
            )
        },
        operation_summary="User Login",
        operation_description="Authenticate a user and return JWT tokens."
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            success=True,
            message="Login successful.",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "phone_number": getattr(user, 'phone_number', None),
                }
            },
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        responses={200: "Logout successful."},
        operation_summary="User Logout",
        operation_description="Logs out the authenticated user."
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response(
            success=True,
            message="Logout successful.",
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        responses={200: UserProfileSerializer},
        operation_summary="Get Profile",
        operation_description="Retrieve the current authenticated user's profile."
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(
            success=True,
            message="User profile retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        operation_summary="Update User Profile",
        operation_description="Update the authenticated user's profile, including uploading a profile picture."
    )
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser])
    def update_profile(self, request):
        """
        Update the current user's profile.
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            message="Profile updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: "Password changed successfully."},
        operation_summary="Change Password",
        operation_description="Change the authenticated user's password."
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def user_change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            success=True,
            message="Password changed successfully.",
            status_code=status.HTTP_200_OK
        )
