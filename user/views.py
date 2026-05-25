import logging

from django.contrib.auth import authenticate, get_user_model
from django.db import DatabaseError, IntegrityError
from rest_framework import permissions, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import (
    LoginRequestSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_serializer():
    try:
        from .serializer import UserSerializer
    except Exception as exc:
        logger.exception("Could not import user.serializer.UserSerializer: %s", exc)
        try:
            from .serializer import UserSerializer
        except Exception as exc:
            logger.exception("Could not import user.serializers.UserSerializer: %s", exc)
            return DefaultUserSerializer
    return UserSerializer


class DefaultUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = tuple(
            field_name
            for field_name in ("id", "username", "email", "first_name", "last_name")
            if any(field.name == field_name for field in User._meta.get_fields())
        ) + ("password",)
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


<<<<<<< HEAD
try:
    from .serializer import UserSerializer as ProjectUserSerializer
except ImportError:
    ProjectUserSerializer = DefaultUserSerializer

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: OpenApiResponse(description="Login successful."),
            400: OpenApiResponse(description="Invalid credentials or missing fields."),
            403: OpenApiResponse(description="User account is disabled."),
        },
    )
=======
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

>>>>>>> 088dcf3 (fix)
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

<<<<<<< HEAD
<<<<<<< muhammadayub
def _service_accepts_single_payload(create_user):
    params = list(inspect.signature(create_user).parameters.values())
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params):
        return False
    positional = [
        param
        for param in params
        if param.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    return len(positional) == 1
=======
            has_email_field = any(
                field.name == "email" for field in User._meta.get_fields()
            )
            if user is None and has_email_field and "@" in str(login_value):
                try:
                    user_obj = User.objects.get(email__iexact=login_value)
                except User.DoesNotExist:
                    user_obj = None
>>>>>>> 088dcf3 (fix)

                if user_obj is not None:
                    user = authenticate(
                        request,
                        username=getattr(user_obj, User.USERNAME_FIELD),
                        password=password,
                    )

<<<<<<< HEAD
def _create_user(serializer):
    if UserService is None or not hasattr(UserService, "create_user"):
        return serializer.save()
=======
=======
>>>>>>> 088dcf3 (fix)
            if user is None:
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
<<<<<<< HEAD
>>>>>>> local
=======
>>>>>>> 088dcf3 (fix)

            if not user.is_active:
                return Response(
                    {"detail": "User account is disabled."},
                    status=status.HTTP_403_FORBIDDEN,
                )

<<<<<<< HEAD
<<<<<<< muhammadayub
    if _service_accepts_single_payload(create_user):
        return create_user(validated_data)
    return create_user(**validated_data)

=======
            UserSerializerClass = get_user_serializer()
            try:
                user_data = UserSerializerClass(user).data
            except Exception as exc:
                logger.exception("Could not serialize login user response: %s", exc)
                user_data = DefaultUserSerializer(user).data
            data = {"user": user_data}

            try:
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken.for_user(user)
                data["refresh"] = str(refresh)
                data["access"] = str(refresh.access_token)
            except Exception as exc:
                logger.warning("JWT tokens were not issued for login: %s", exc)
>>>>>>> local
=======
            UserSerializer = get_user_serializer()
            try:
                user_data = UserSerializer(user).data
            except Exception as exc:
                logger.exception("Could not serialize login user response: %s", exc)
                user_data = DefaultUserSerializer(user).data
            data = {"user": user_data}

            try:
                from rest_framework_simplejwt.tokens import RefreshToken
            except ImportError:
                pass
            else:
                refresh = RefreshToken.for_user(user)
                data["refresh"] = str(refresh)
                data["access"] = str(refresh.access_token)
>>>>>>> 088dcf3 (fix)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Login API unexpected error: %s", exc)
            return Response(
                {
                    "detail": "Login failed because of an internal server error.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )
    def post(self, request, *args, **kwargs):
<<<<<<< HEAD
<<<<<<< muhammadayub
=======
        UserSerializer = get_user_serializer()
>>>>>>> 088dcf3 (fix)
        serializer = UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
=======
        UserSerializerClass = get_user_serializer()
        serializer = UserSerializerClass(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                UserSerializerClass(user).data,
                status=status.HTTP_201_CREATED,
            )
>>>>>>> local
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

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, *args, **kwargs):
<<<<<<< HEAD
<<<<<<< muhammadayub
        if not request.user.is_authenticated:
            return _auth_required_response()
=======
        UserSerializer = get_user_serializer()
>>>>>>> 088dcf3 (fix)
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
=======
        UserSerializerClass = get_user_serializer()
        return Response(
            UserSerializerClass(request.user).data,
            status=status.HTTP_200_OK,
        )
>>>>>>> local


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "old_password": {"type": "string"},
                    "new_password": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["new_password"],
            }
        },
        responses={200: OpenApiResponse(description="Password changed successfully.")},
    )
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
        return Response({"detail": "Password changed successfully."})


class ChangeUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]

<<<<<<< HEAD
<<<<<<< muhammadayub
    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _auth_required_response()

=======
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"username": {"type": "string"}},
                "required": ["username"],
            }
        },
        responses={200: OpenApiResponse(description="Username updated.")},
    )
    def post(self, request, *args, **kwargs):
        return self._update_username(request)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"username": {"type": "string"}},
                "required": ["username"],
            }
        },
        responses={200: OpenApiResponse(description="Username updated.")},
    )
    def patch(self, request, *args, **kwargs):
        return self._update_username(request)

    def _update_username(self, request):
>>>>>>> local
=======
    def post(self, request, *args, **kwargs):
>>>>>>> 088dcf3 (fix)
        username = request.data.get("username")
        if not username:
            return Response(
                {"username": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.exclude(pk=request.user.pk).filter(username=username).exists():
            return Response(
                {"username": ["A user with that username already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.username = username
        request.user.save(update_fields=["username"])
        return Response({"username": request.user.username}, status=status.HTTP_200_OK)

<<<<<<< HEAD
<<<<<<< muhammadayub

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ("create", "register"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        view = RegisterView()
        view.request = request
        return view.post(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="register",
    )
    def register(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request, *args, **kwargs):
        view = MeView()
        if request.method.lower() == "patch":
            return view.patch(request, *args, **kwargs)
        return view.get(request, *args, **kwargs)


class GenericJSONView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Endpoint is not implemented."}, status=501)

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Endpoint is not implemented."}, status=501)

=======
>>>>>>> 088dcf3 (fix)
    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

=======
>>>>>>> local

LoginAPIView = LoginView
RegisterAPIView = RegisterView
UserRegisterView = RegisterView
UserRegistrationView = RegisterView
ProfileView = MeView
UserProfileView = MeView
CurrentUserView = MeView
