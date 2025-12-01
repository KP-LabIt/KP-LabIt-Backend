from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import User, Role
from .serializer import UserSerializer, RoleSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

# view pre veci ohladne usera/accounts
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    if not old_password or not new_password:
        return Response({"detail": "Old and new password required."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.must_change_password = False
    user.save()
    return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


# tento JWT login endpoint: POST /api/login/ s {"email", "password"} vráti JWT s firstName, lastName, role
@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if not email or not password:
        return Response({"detail": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    # Authenticate using username, since default backend does not support email
    user_auth = authenticate(username=user.username, password=password)
    if user_auth is None:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    # role sú uložené priamo v User modeli (ForeignKey na Role) -> user.role.name
    if user.role:
        role = user.role.name
    else:
        role = "student"

    payload = {
        "firstName": user.first_name,
        "lastName": user.last_name,
        "role": role
    }
    refresh = RefreshToken.for_user(user)
    # pridať vlastné claimy
    for k, v in payload.items():
        refresh[k] = v
    jwt_token = str(refresh.access_token)
    return Response({
        "token": jwt_token,
        "must_change_password": user.must_change_password
    })

@api_view(["GET"])
def get_init(request):
    return Response("Endpoint pre accounts...")