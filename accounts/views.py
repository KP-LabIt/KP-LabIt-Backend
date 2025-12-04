from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils.timezone import now
from djoser.views import UserViewSet
from .models import User, Role
from .serializer import UserSerializer, RoleSerializer
from .permissions import IsAuthenticatedWithValidToken
from .ms_graph import MicrosoftGraphClient
import logging

logger = logging.getLogger(__name__)

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


@api_view(["POST"])
@permission_classes([AllowAny])  # Public endpoint - does not require access token
def refresh_token(request):
    """
    Refresh access token endpoint.
    Takes refresh_token and returns new access_token.
    Does NOT require access token - only valid refresh token.
    """
    refresh_token_str = request.data.get("refresh_token")
    
    if not refresh_token_str:
        return Response({
            "detail": "Refresh token required.",
            "code": "missing_refresh_token"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate refresh token
        refresh = RefreshToken(refresh_token_str)
        
        # Get user from token
        user_id = refresh.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "detail": "User not found.",
                "code": "user_not_found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get user role
        if user.role:
            role = user.role.name
        else:
            role = "student"
        
        # Create new access token with user information
        payload = {
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": role,
            "email": user.email,
            "username": user.username
        }
        
        # Generate new refresh token (optional - can reuse old one)
        new_refresh = RefreshToken.for_user(user)
        for k, v in payload.items():
            new_refresh[k] = v
        
        new_access_token = str(new_refresh.access_token)
        new_refresh_token = str(new_refresh)
        
        return Response({
            "token": new_access_token,
            "refresh_token": new_refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "role": role
            }
        }, status=status.HTTP_200_OK)
        
    except TokenError as e:
        return Response({
            "detail": "Invalid or expired refresh token.",
            "code": "invalid_refresh_token"
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            "detail": "Token refresh failed.",
            "code": "refresh_failed"
        }, status=status.HTTP_400_BAD_REQUEST)


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

# Microsoft Authentication Views
@api_view(['GET'])
@permission_classes([AllowAny])
def microsoft_login(request):
    """
    Initiate Microsoft OAuth2 login.
    
    GET /api/accounts/microsoft/login/
    
    This endpoint redirects the user to social-auth's login URL which handles
    the OAuth2 flow automatically.
    
    Returns:
        Redirect to social-auth Microsoft OAuth2 login
    """
    try:
        logger.info("Redirecting to Microsoft OAuth2 login")
        return redirect('/login/microsoft-oauth2/')
    except Exception as e:
        logger.error(f"Microsoft login failed: {str(e)}")
        return JsonResponse({
            'error': 'Failed to initiate Microsoft login',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_success(request):
    """
    Success endpoint after Microsoft OAuth2 authentication.
    
    GET /api/accounts/auth/success/
    
    This endpoint is called after successful Microsoft authentication.
    It generates JWT tokens and redirects to frontend with tokens.
    
    Returns:
        Redirect to frontend with JWT tokens in URL parameters
    """
    try:
        if request.user.is_authenticated:
            user = request.user
            
            # Generate JWT token for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token_str = str(refresh)
            
            logger.info(f"Microsoft authentication successful for user: {user.email if hasattr(user, 'email') else user.username}")
            
            # Redirect to frontend with tokens
            frontend_url = f"http://localhost:5173/auth/callback?token={access_token}&refresh_token={refresh_token_str}"
            return redirect(frontend_url)
        else:
            logger.warning("Authentication failed - user not authenticated")
            # Redirect to frontend with error
            return redirect('http://localhost:5173/login?error=authentication_failed')
    except Exception as e:
        logger.error(f"Auth success error: {str(e)}")
        # Redirect to frontend with error
        return redirect(f'http://localhost:5173/login?error=processing_failed&detail={str(e)}')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_microsoft_users(request):
    """
    Fetch users from Microsoft Graph API.
    
    GET /api/accounts/microsoft/users/
    
    This endpoint uses Client Credentials flow (app-only access) to fetch
    users from Microsoft Graph API.
    
    Query Parameters:
        top (int, optional): Limit number of users (e.g., ?top=10)
        select (str, optional): Comma-separated list of properties 
                               (e.g., ?select=displayName,mail,id)
    
    Returns:
        JSON response with list of users from Microsoft Graph
    """
    try:
        graph_client = MicrosoftGraphClient()
        
        # Get query parameters
        top = request.GET.get('top')
        select = request.GET.get('select')
        
        # Parse parameters
        top_int = int(top) if top and top.isdigit() else None
        select_list = select.split(',') if select else None
        
        # Fetch users from Microsoft Graph
        users_data = graph_client.get_users(top=top_int, select=select_list)
        users = users_data.get('value', [])
        
        logger.info(f"Successfully fetched {len(users)} users from Microsoft Graph API")
        
        return JsonResponse({
            'status': 'success',
            'count': len(users),
            'users': users,
            'odata_context': users_data.get('@odata.context'),
            'next_link': users_data.get('@odata.nextLink'),
        }, status=200)
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': 'Configuration error',
            'detail': str(e),
            'help': 'Please ensure TENANT_ID, CLIENT_ID, and CLIENT_SECRET are set in .env file'
        }, status=500)
    except Exception as e:
        logger.error(f"Failed to fetch Microsoft users: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': 'Failed to fetch users from Microsoft Graph',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_microsoft_user_by_id(request, user_id):
    """
    Fetch a specific user by ID from Microsoft Graph API.
    
    GET /api/accounts/microsoft/users/<user_id>/
    
    Args:
        user_id (str): Microsoft user ID or userPrincipalName
    
    Query Parameters:
        select (str, optional): Comma-separated list of properties
    
    Returns:
        JSON response with user details
    """
    try:
        graph_client = MicrosoftGraphClient()
        
        select = request.GET.get('select')
        select_list = select.split(',') if select else None
        
        user_data = graph_client.get_user_by_id(user_id, select=select_list)
        
        logger.info(f"Successfully fetched user: {user_id}")
        
        return JsonResponse({
            'status': 'success',
            'user': user_data
        }, status=200)
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': 'Failed to fetch user from Microsoft Graph',
            'detail': str(e)
        }, status=500)