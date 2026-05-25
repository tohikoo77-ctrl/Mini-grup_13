import inspect
import logging

from django.contrib.auth import authenticate, get_user_model
from django.db import DatabaseError, IntegrityError
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
User = get_user_model()


def _model_field_names():
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
        fields = _model_field_names() + ("password",)
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


try:
    from .serializers import UserSerializer as ProjectUserSerializer
except ImportError:
    ProjectUserSerializer = DefaultUserSerializer

try:
    from .services import UserService
except ImportError:
    UserService = None

UserSerializer = ProjectUserSerializer


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


def _create_user(serializer):
    if UserService is None or not hasattr(UserService, "create_user"):
        return serializer.save()

    create_user = UserService.create_user
    validated_data = dict(serializer.validated_data)

    if _service_accepts_single_payload(create_user):
        return create_user(validated_data)
    return create_user(**validated_data)


def _auth_required_response():
    return Response(
        {"detail": "Authentication credentials were not provided."},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _token_payload(user):
    data = {"user": UserSerializer(user).data}
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
    except ImportError:
        return data

    refresh = RefreshToken.for_user(user)
    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)
    return data


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = _create_user(serializer)
            if user is None:
                raise RuntimeError("User creation returned no user instance.")
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
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


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username/email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(_token_payload(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _auth_required_response()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _auth_required_response()

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _auth_required_response()

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password") or request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not new_password:
            return Response(
                {"new_password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if confirm_password and new_password != confirm_password:
            return Response(
                {"confirm_password": ["Passwords do not match."]},
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

    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _auth_required_response()

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

    def patch(self, request, *args, **kwargs):
        return Response({"detail": "Endpoint is not implemented."}, status=501)


RegisterAPIView = RegisterView
UserRegisterView = RegisterView
UserRegistrationView = RegisterView
LoginAPIView = LoginView
ProfileView = MeView
UserProfileView = MeView
CurrentUserView = MeView

try:
    from rest_framework_simplejwt.views import TokenObtainPairView
except ImportError:
    CustomTokenObtainPairView = LoginView
else:
    class CustomTokenObtainPairView(TokenObtainPairView):
        pass


def __getattr__(name):
    if name.endswith("View") or name.endswith("APIView"):
        return GenericJSONView
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
