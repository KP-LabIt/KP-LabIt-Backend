"""
Custom permission classes for comprehensive token validation and role-based access control.

Every endpoint (except login) must validate:
1. Token is present in request
2. Token is valid and was created by backend
3. Token is not expired
4. User has the correct role for the endpoint
"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime


class IsAuthenticatedWithValidToken(BasePermission):
    """
    Base permission class that performs full token validation.
    All custom role-based permissions inherit from this class.
    
    Validates:
    - User is authenticated
    - Token is present and properly formatted
    - Token was created by backend (valid signature)
    - Token is not expired
    - Token user_id matches authenticated user
    """
    
    def has_permission(self, request, view):
        # Step 1: Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed({
                "detail": "Authentication credentials were not provided.",
                "code": "no_token"
            })
        
        # Step 2: Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed({
                "detail": "Invalid token header. Token must be provided as 'Bearer <token>'.",
                "code": "invalid_token_header"
            })
        
        token_string = auth_header.split(' ')[1]
        
        try:
            # Step 3: Validate token and check if it was created by backend
            token = AccessToken(token_string)
            
            # Step 4: Check if token is expired
            exp_timestamp = token.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                if datetime.now() > exp_datetime:
                    raise AuthenticationFailed({
                        "detail": "Token has expired. Please login again.",
                        "code": "token_expired"
                    })
            
            # Step 5: Verify token user_id matches authenticated user
            token_user_id = str(token.get('user_id'))
            if token_user_id != str(request.user.id):
                raise AuthenticationFailed({
                    "detail": "Token user mismatch.",
                    "code": "token_user_mismatch"
                })
            
            return True
            
        except TokenError as e:
            raise AuthenticationFailed({
                "detail": f"Token is invalid: {str(e)}",
                "code": "invalid_token"
            })
        except InvalidToken as e:
            raise AuthenticationFailed({
                "detail": f"Token is invalid: {str(e)}",
                "code": "invalid_token"
            })
        except Exception as e:
            raise AuthenticationFailed({
                "detail": f"Token validation failed: {str(e)}",
                "code": "token_validation_failed"
            })


class IsStudent(IsAuthenticatedWithValidToken):
    """
    Permission for student-only endpoints.
    Performs full token validation + checks user has 'student' role.
    """
    
    def has_permission(self, request, view):
        # First perform full token validation
        if not super().has_permission(request, view):
            return False
        
        # Check if user has student role
        if not hasattr(request.user, 'role') or not request.user.role:
            raise PermissionDenied({
                "detail": "User does not have a role assigned.",
                "code": "no_role"
            })
        
        if request.user.role.name.lower() != 'student':
            raise PermissionDenied({
                "detail": "This endpoint is only accessible to students.",
                "code": "not_student"
            })
        
        return True


class IsTeacher(IsAuthenticatedWithValidToken):
    """
    Permission for teacher-only endpoints.
    Performs full token validation + checks user has 'teacher' role.
    """
    
    def has_permission(self, request, view):
        # First perform full token validation
        if not super().has_permission(request, view):
            return False
        
        # Check if user has teacher role
        if not hasattr(request.user, 'role') or not request.user.role:
            raise PermissionDenied({
                "detail": "User does not have a role assigned.",
                "code": "no_role"
            })
        
        if request.user.role.name.lower() != 'teacher':
            raise PermissionDenied({
                "detail": "This endpoint is only accessible to teachers.",
                "code": "not_teacher"
            })
        
        return True


class IsAdmin(IsAuthenticatedWithValidToken):
    """
    Permission for admin-only endpoints.
    Performs full token validation + checks user has 'admin' role or is superuser.
    """
    
    def has_permission(self, request, view):
        # First perform full token validation
        if not super().has_permission(request, view):
            return False
        
        # Superuser always has access
        if request.user.is_superuser:
            return True
        
        # Check if user has admin role
        if not hasattr(request.user, 'role') or not request.user.role:
            raise PermissionDenied({
                "detail": "User does not have a role assigned.",
                "code": "no_role"
            })
        
        if request.user.role.name.lower() != 'admin':
            raise PermissionDenied({
                "detail": "This endpoint is only accessible to administrators.",
                "code": "not_admin"
            })
        
        return True


class IsTeacherOrAdmin(IsAuthenticatedWithValidToken):
    """
    Permission for endpoints accessible to teachers and admins.
    Performs full token validation + checks user has 'teacher' or 'admin' role.
    """
    
    def has_permission(self, request, view):
        # First perform full token validation
        if not super().has_permission(request, view):
            return False
        
        # Superuser always has access
        if request.user.is_superuser:
            return True
        
        # Check if user has teacher or admin role
        if not hasattr(request.user, 'role') or not request.user.role:
            raise PermissionDenied({
                "detail": "User does not have a role assigned.",
                "code": "no_role"
            })
        
        role_name = request.user.role.name.lower()
        if role_name not in ['teacher', 'admin']:
            raise PermissionDenied({
                "detail": "This endpoint is only accessible to teachers and administrators.",
                "code": "insufficient_permissions"
            })
        
        return True


class IsStudentOrTeacher(IsAuthenticatedWithValidToken):
    """
    Permission for endpoints accessible to students and teachers.
    Performs full token validation + checks user has 'student' or 'teacher' role.
    """
    
    def has_permission(self, request, view):
        # First perform full token validation
        if not super().has_permission(request, view):
            return False
        
        # Superuser always has access
        if request.user.is_superuser:
            return True
        
        # Check if user has student or teacher role
        if not hasattr(request.user, 'role') or not request.user.role:
            raise PermissionDenied({
                "detail": "User does not have a role assigned.",
                "code": "no_role"
            })
        
        role_name = request.user.role.name.lower()
        if role_name not in ['student', 'teacher']:
            raise PermissionDenied({
                "detail": "This endpoint is only accessible to students and teachers.",
                "code": "insufficient_permissions"
            })
        
        return True
