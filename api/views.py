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


# tento endpoint vrati vsetky rezervacie pre aktualne prihlaseneho usera
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_user_reservations(request):
    
    user = request.user
    reservations = Reservation.objects.filter(user=user)

    serializer = ReservationSerializer(reservations, many=True)

    # doplnenie user dat do kazdej rezervacie, lebo serializer to sam neobsahuje
    for data in serializer.data:
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name if user.role else None
        }

        
    return Response(serializer.data)


#tento endpoint zmaze rezervaciu pre aktualne prihlaseneho usera
@api_view(["DELETE"])
@permission_classes([IsAuthenticatedWithValidToken])
def delete_reservation(request, reservation_id):
    user = request.user

    try:
        reservation = Reservation.objects.get(id=reservation_id, user=user)
    except Reservation.DoesNotExist:
        return Response({"error": "Rezervácia neexistuje alebo nemáte oprávnenie ju zmazať."}, status=status.HTTP_404_NOT_FOUND)

    reservation.delete()
    return Response({"detail": "Rezervácia bola úspešne zmazaná."}, status=status.HTTP_200_OK)