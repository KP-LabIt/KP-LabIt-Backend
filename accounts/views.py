from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Role
from .serializer import UserSerializer, RoleSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# view pre veci ohladne usera/accounts


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

    user_auth = authenticate(email=email, password=password)
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
    return Response({"token": jwt_token})

@api_view(["GET"])
def get_init(request):
    return Response("Endpoint pre accounts...")