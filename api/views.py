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
from django.utils import timezone


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


# tento endpoint vrati vsetky rezervacie, ktore ma študent, alebo všetky rezervacie, ktoré ma učiteľ pre svoje aktivity
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_user_reservations(request):
    user = request.user
    now = timezone.now()

    if user.role and user.role.name == "teacher":
        reservations = Reservation.objects.filter(
            activity_slot__teacher=user,
            activity_slot__end_date__gte=now  # iba tie rezervacie, ktore este neprebehli
        ).select_related(
            "user",
            "activity_slot",
            "activity_slot__activity"
        )
    else:
        reservations = Reservation.objects.filter(
            user=user,
            activity_slot__end_date__gte=now  # iba tie rezervacie, ktore este neprebehli
        ).select_related(
            "user",
            "activity_slot",
            "activity_slot__activity"
        )


    serializer = ReservationSerializer(
        reservations,
        many=True,
        context={"request": request}
    )


    return Response(serializer.data)


# tento endpoint zmeni status rezervacie (len pre ucitelov, ktori su priradeni k danej aktivite)
@api_view(["PATCH"])
@permission_classes([IsTeacher])
def change_reservation_status(request, reservation_id):
    user = request.user
    try:
        reservation = Reservation.objects.get(id=reservation_id, activity_slot__teacher=user)
    except Reservation.DoesNotExist:
        return Response({"error": "Rezervácia neexistuje alebo nemáte právo ju upraviť."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status not in Reservation.Status.values:
        return Response({"error": "Neplatný status."}, status=status.HTTP_400_BAD_REQUEST)

    reservation.status = new_status
    reservation.save()


    return Response({"detail": "Status rezervácie bol úspešne zmenený."}, status=status.HTTP_200_OK)


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