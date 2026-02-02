from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Activity, ActivitySlot, Reservation
from .serializer import ActivitySerializer, ActivitySlotSerializer, ReservationSerializer, ActivityWithSlotsSerializer, CreateReservationSerializer
from accounts.permissions import (
    IsAuthenticatedWithValidToken,
    IsStudent,
    IsTeacher,
    IsTeacherOrAdmin,
    IsStudentOrTeacher
)
from django.utils import timezone
from django.utils.dateparse import parse_datetime


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


# tento endpoint vytvori novu rezervaciu (studenti, ucitelia, admini)
@api_view(["POST"])
@permission_classes([IsAuthenticatedWithValidToken])
def create_reservation(request):
    """
    Vytvorí novú rezerváciu pre aktuálne prihláseného používateľa.
    Študenti môžu rezervovať len aktivity pre svoju rolu, učitelia/admini môžu rezervovať akúkoľvek aktivitu.
    
    Validácia:
    1. Overí existenciu activity_slot
    2. Overí, že slot je v budúcnosti
    3. Overí role-based prístup (študenti len svoje aktivity)
    4. Overí, že kapacita nie je prekročená
    5. Overí, že používateľ už nemá rezerváciu pre tento slot
    6. Vytvorí rezerváciu so statusom PENDING
    """
    user = request.user
    serializer = CreateReservationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Serializer už validoval a načítal activity_slot objekt
    activity_slot = serializer.validated_data.get('activity_slot')
    note = serializer.validated_data.get('note', '')
    
    # Načítame activity s role pre validáciu (select_related pre optimalizáciu)
    try:
        activity_slot = ActivitySlot.objects.select_related('activity', 'activity__role').get(id=activity_slot.id)
    except ActivitySlot.DoesNotExist:
        return Response({"error": "Časový slot neexistuje."}, status=status.HTTP_404_NOT_FOUND)
    
    activity = activity_slot.activity
    now = timezone.now()
    
    # Validácia 1: Overenie, že slot je v budúcnosti (ešte nezačal)
    if activity_slot.start_date <= now:
        return Response({
            "error": "Nie je možné rezervovať slot, ktorý už začal alebo skončil."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validácia 2: Overenie role-based prístupu (študenti len aktivity pre svoju rolu)
    if user.role and user.role.name == "student":
        if activity.role != user.role:
            return Response({
                "error": "Nemáte oprávnenie rezervovať túto aktivitu."
            }, status=status.HTTP_403_FORBIDDEN)
    
    # Validácia 3: Overenie kapacity
    # Počítame len rezervácie, ktoré nie sú zrušené
    existing_reservations = Reservation.objects.filter(
        activity_slot=activity_slot
    ).exclude(status=Reservation.Status.CANCELLED)
    
    reserved_count = existing_reservations.count()
    
    if reserved_count >= activity.capacity:
        return Response({
            "error": f"Kapacita aktivity je naplnená ({reserved_count}/{activity.capacity})."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validácia 4: Overenie, že používateľ už nemá rezerváciu pre tento slot
    existing_user_reservation = Reservation.objects.filter(
        user=user,
        activity_slot=activity_slot
    ).exclude(status=Reservation.Status.CANCELLED)
    
    if existing_user_reservation.exists():
        return Response({
            "error": "Už máte aktívnu rezerváciu pre tento časový slot."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vytvorenie rezervácie
    reservation = Reservation.objects.create(
        user=user,
        activity_slot=activity_slot,
        note=note,
        status=Reservation.Status.PENDING
    )
    
    # Serializácia výsledku pre odpoveď
    result_serializer = ReservationSerializer(reservation, context={"request": request})
    
    return Response({
        "detail": "Rezervácia bola úspešne vytvorená a čaká na schválenie.",
        "reservation": result_serializer.data
    }, status=status.HTTP_201_CREATED)


# tento endpoint vrati vsetky aktivity (studenti vidi len aktivity pre svoju rolu, ucitelia/admini vidi vsetky)
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_activities(request):
    """
    Vráti všetky aktivity.
    Študenti vidia len aktivity pre svoju rolu, učitelia/admini vidia všetky aktivity.
    """
    user = request.user

    if user.role and user.role.name in ["teacher", "admin"]:
        # ucitelia a admini vidi vsetky aktivity
        activities = Activity.objects.all()
    else:
        # studenti vidi len aktivity pre svoju rolu
        activities = Activity.objects.filter(role=user.role)

    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)


# tento endpoint vytvori novu aktivitu (len pre ucitelov a adminov)
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def create_activity(request):
    """
    Vytvorí novú aktivitu.
    Vyžaduje rolu učiteľa alebo administrátora.
    """
    serializer = ActivitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "detail": "Aktivita bola úspešne vytvorená.",
            "activity": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# tento endpoint vrati vsetky aktivity (studenti vidi len aktivity pre svoju rolu, ucitelia/admini vidi vsetky)
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_activities(request):
    """
    Vráti všetky aktivity.
    Študenti vidia len aktivity pre svoju rolu, učitelia/admini vidia všetky aktivity.
    """
    user = request.user

    if user.role and user.role.name in ["teacher", "admin"]:
        # ucitelia a admini vidi vsetky aktivity
        activities = Activity.objects.all()
    else:
        # studenti vidi len aktivity pre svoju rolu
        activities = Activity.objects.filter(role=user.role)

    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)

# endpoint pre získanie aktivity slotov pre rezervation page
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_activity_slots(request, activity_id, start_date, end_date):
    """
    Vráti sloty pre konkrétnu aktivitu v zadanom časovom rozsahu.
    Tento endpoint používa frontend pre rezervačnú stránku.

    Logika:
    1. Overí existenciu aktivity.
    2. Vyfiltruje sloty prislúchajúce k danej aktivite a spadajúce do rozsahu start_date - end_date.
    3. Serializuje dáta vrátane počtu rezervácií a informácie o naplnení kapacity.
    """
    try:
        # Skúsime nájsť aktivitu podľa ID
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({"error": "Aktivita nebola nájdená."}, status=status.HTTP_404_NOT_FOUND)

    # Parse datetime values from incoming params. Expected format: 2026-01-02T22:10:28+01:00
    start_dt = parse_datetime(start_date)
    end_dt = parse_datetime(end_date)
    if start_dt is None or end_dt is None:
        return Response({"error": "Neplatný formát dátumu a času."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure timezone-aware datetimes
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
    if timezone.is_naive(end_dt):
        end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())

    # Filtrovanie slotov podľa aktivity a časového rozsahu s presnosťou na čas
    slots = ActivitySlot.objects.filter(
        activity=activity,
        start_date__gte=start_dt,
        end_date__lte=end_dt
    ).select_related('activity')

    # Serializácia základných údajov o aktivite (použijeme ActivitySerializer pre konzistentný formát)
    activity_data = ActivitySerializer(activity).data

    # Príprava výsledného zoznamu s vypočítanými poliami
    result = []
    for slot in slots:
        # Spočítame všetky rezervácie pre tento slot, ktoré nie sú zrušené
        reserved_count = slot.reservation_set.exclude(status=Reservation.Status.CANCELLED).count()

        # Určíme, či je kapacita naplnená
        is_full = reserved_count >= activity.capacity

        result.append({
            "slotId": slot.id,
            "start_date": slot.start_date.isoformat(),
            "end_date": slot.end_date.isoformat(),
            "activity": activity_data,
            "reservedCount": reserved_count,
            "isFull": is_full
        })

    return Response(result)

# endpoint pre vytvorenie aktivity a prislusnymi aktivity slotmi naraz
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def create_activity_with_slots(request):

    serializer = ActivityWithSlotsSerializer(
        data=request.data,
        context={"request": request}  # so serializer can access request.user
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            "detail": "Aktivita a Termíny, boli úspešne vytvorené!"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
