import logging

from django.contrib.auth import authenticate, get_user_model
from django.db import DatabaseError, IntegrityError
from rest_framework import permissions, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


logger = logging.getLogger(__name__)
User = get_user_model()


def user_field_names():
    names = []
    for field_name in ("id", "username", "email", "first_name", "last_name"):
        try:
            User._meta.get_field(field_name)
        except Exception:
            continue
        names.append(field_name)
    return tuple(names)


class DefaultUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = user_field_names() + ("password",)
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if hasattr(User.objects, "create_user"):
            return User.objects.create_user(password=password, **validated_data)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


def get_user_serializer():
    try:
        from .serializer import UserSerializer

        return UserSerializer
    except Exception as exc:
        logger.exception("Could not import user.serializer.UserSerializer: %s", exc)

    try:
        from .serializers import UserSerializer

        return UserSerializer
    except Exception as exc:
        logger.exception("Could not import user.serializers.UserSerializer: %s", exc)

    return DefaultUserSerializer


def serialize_user(user):
    UserSerializer = get_user_serializer()

    try:
        return UserSerializer(user).data
    except Exception as exc:
        logger.exception("Could not serialize user with project serializer: %s", exc)
        return DefaultUserSerializer(user).data


def build_token_response(user):
    data = {"user": serialize_user(user)}

    try:
        from rest_framework_simplejwt.tokens import RefreshToken
    except ImportError:
        return data

    refresh = RefreshToken.for_user(user)
    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)
    return data


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        try:
            login_value = (
                request.data.get("username")
                or request.data.get("email")
                or request.data.get("phone")
            )
            password = request.data.get("password")

            if not login_value or not password:
                return Response(
                    {
                        "detail": "username/email and password are required.",
                        "fields": {
                            "username": "required if email is not sent",
                            "email": "required if username is not sent",
                            "password": "required",
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = authenticate(request, username=login_value, password=password)

            if user is None and "@" in str(login_value):
                user = self.authenticate_by_email(request, login_value, password)

            if user is None:
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.is_active:
                return Response(
                    {"detail": "User account is disabled."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(build_token_response(user), status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Login API unexpected error: %s", exc)
            return Response(
                {
                    "detail": "Login failed because of an internal server error.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def authenticate_by_email(self, request, email, password):
        try:
            User._meta.get_field("email")
        except Exception:
            return None

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

        username = getattr(user_obj, User.USERNAME_FIELD)
        return authenticate(request, username=username, password=password)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        UserSerializer = get_user_serializer()
        serializer = UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(serialize_user(user), status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as exc:
            logger.exception("Register API integrity error: %s", exc)
            return Response(
                {"detail": "Registration failed.", "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DatabaseError as exc:
            logger.exception("Register API database error: %s", exc)
            return Response(
                {
                    "detail": "Registration failed because of a database error.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as exc:
            logger.exception("Register API unexpected error: %s", exc)
            return Response(
                {
                    "detail": "Registration failed because of an internal server error.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(serialize_user(request.user), status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password") or request.data.get("password")

        if not new_password:
            return Response(
                {"new_password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if old_password and not request.user.check_password(old_password):
            return Response(
                {"old_password": ["Old password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class ChangeUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")

        if not username:
            return Response(
                {"username": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username_exists = (
            User.objects.exclude(pk=request.user.pk).filter(username=username).exists()
        )
        if username_exists:
            return Response(
                {"username": ["A user with that username already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.username = username
        request.user.save(update_fields=["username"])
        return Response({"username": request.user.username}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


LoginAPIView = LoginView
RegisterAPIView = RegisterView
UserRegisterView = RegisterView
UserRegistrationView = RegisterView
ProfileView = MeView
UserProfileView = MeView
CurrentUserView = MeView
