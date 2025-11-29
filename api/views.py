from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Test
from .serializer import TestSerializer
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

    user_auth = authenticate(username=user.username, password=password)
    if user_auth is None:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    #predpokladanie že role su uložené v user.profile.role alebo podobnom poli ak tam nie je použije sa predvolená hodnota user.
    role = getattr(getattr(user, 'profile', None), 'role', 'user')
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



# tento endpoint vráti všetky obejkty, ktoré su v Test tabulke.
@api_view(["GET"])
def get_data(request):
    data = Test.objects.all()
    serialized_data = TestSerializer(data, many=True).data
    return Response(serialized_data)

# tento endpoint vytvorí nový obejkt v Test tabuľke, ak sú správne údaje valid(očakava sa meno a body).
@api_view(["POST"])
def post_test(request):
    data = request.data
    serializer = TestSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# default endpoint, nepotrebny, iba na testovanie.
@api_view(["GET"])
def get_init(request):
    return Response("Endpoint pre api...") 


