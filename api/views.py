from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Activity, ActivitySlot, Reservation
from .serializer import ActivitySerializer, ActivitySlotSerializer, ReservationSerializer
from accounts.permissions import (
    IsAuthenticatedWithValidToken,
    IsStudent,
    IsTeacher,
    IsTeacherOrAdmin,
    IsStudentOrTeacher
)

# view pre vseobecne api veci ako aktivity, rezervacie atd(keby bol v tom chaos, tak sa vie popripadne spravit pre kazdu vec vlastna appka
# napr. že už mame pre accounts appku, tak vieme spraviť aj čisto pre rezervacie, a potom pre aktivity...)


@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_init(request):
    """
    Test endpoint - requires valid JWT token.
    Token is validated, decrypted, checked for:
    - Presence and proper format
    - Valid signature (created by backend)
    - Not expired
    - User authentication
    """
    return Response({
        "detail": "Endpoint pre api...",
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "role": request.user.role.name if request.user.role else None
        }
    })

