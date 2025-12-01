from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import User, Role
from .serializer import UserSerializer, RoleSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .permissions import IsAuthenticatedWithValidToken
from djoser.views import UserViewSet
from rest_framework.decorators import action
from django.utils.timezone import now

# view pre veci ohladne usera/accounts
@api_view(["POST"])
@permission_classes([IsAuthenticatedWithValidToken])
def change_password(request):
    """
    Change user password endpoint.
    Requires valid JWT token with full validation:
    - Token must be present
    - Token must be valid and created by backend
    - Token must not be expired
    - User must be authenticated
    """
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    
    if not old_password or not new_password:
        return Response({
            "detail": "Old and new password required.",
            "code": "missing_passwords"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({
            "detail": "Old password is incorrect.",
            "code": "incorrect_old_password"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate new password is different
    if old_password == new_password:
        return Response({
            "detail": "New password must be different from old password.",
            "code": "same_password"
        }, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.must_change_password = False
    user.save()
    
    return Response({
        "detail": "Password changed successfully.",
        "code": "password_changed"
    }, status=status.HTTP_200_OK)


# tento JWT login endpoint: POST /api/login/ s {"email", "password"} vráti JWT s firstName, lastName, role
@api_view(["POST"])
@permission_classes([AllowAny])  # Login does not require token - public endpoint
def login(request):
    """
    Login endpoint - DOES NOT require token (public access).
    Returns JWT token that must be used for all subsequent requests.
    """
    email = request.data.get("email")
    password = request.data.get("password")
    
    if not email or not password:
        return Response({
            "detail": "Email and password required.",
            "code": "missing_credentials"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "detail": "Invalid credentials.",
            "code": "invalid_credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Authenticate using username, since default backend does not support email
    user_auth = authenticate(username=user.username, password=password)
    if user_auth is None:
        return Response({
            "detail": "Invalid credentials.",
            "code": "invalid_credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # role sú uložené priamo v User modeli (ForeignKey na Role) -> user.role.name
    if user.role:
        role = user.role.name
    else:
        role = "student"

    # Create JWT token with user information embedded
    payload = {
        "firstName": user.first_name,
        "lastName": user.last_name,
        "role": role,
        "email": user.email,
        "username": user.username
    }
    refresh = RefreshToken.for_user(user)
    # pridať vlastné claimy
    for k, v in payload.items():
        refresh[k] = v
    
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return Response({
        "token": access_token,
        "refresh_token": refresh_token,
        "must_change_password": user.must_change_password,
        "user": {
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": role
        }
    }, status=status.HTTP_200_OK)


# prepisanie djoser reset_password_confirm view (logika je taká istá, ako v oficialnom github repe tejto knižnice, iba pridavam zmenu polia must_change_password
# ešte som zakomentoval podmienku, kde kontroluje, či mam v settings "PASSWORD_CHANGED_EMAIL_CONFIRMATION", lebo ju nemáme (ak by sme mali, tak by poslal mail po zmene hesla) a vyhadzoval server error(pri importovani tohto default view to ignorovalo nejako))
class CustomUserViewSet(UserViewSet):
    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        serializer.user.must_change_password = False
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        # if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
        #   context = {"user": serializer.user}
        #    to = [get_user_email(serializer.user)]
        #    settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_init(request):
    """
    Test endpoint - requires valid JWT token.
    Token is validated, decrypted, and checked for expiration.
    """
    return Response({
        "detail": "Endpoint pre accounts...",
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "role": request.user.role.name if request.user.role else None
        }
    })