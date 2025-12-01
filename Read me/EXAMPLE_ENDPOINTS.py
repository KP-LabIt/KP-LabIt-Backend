"""
Example API endpoints demonstrating token validation and role-based permissions.
Copy these examples when creating new endpoints in your views.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import (
    IsAuthenticatedWithValidToken,
    IsStudent,
    IsTeacher,
    IsAdmin,
    IsTeacherOrAdmin,
    IsStudentOrTeacher
)
from .models import Activity, ActivitySlot, Reservation
from .serializer import ActivitySerializer, ActivitySlotSerializer, ReservationSerializer


# ============================================================================
# EXAMPLE 1: Endpoint accessible to ALL authenticated users
# ============================================================================
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_user_profile(request):
    """
    Get current user's profile.
    Token is validated - any authenticated user can access.
    """
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.name if user.role else None,
    })


# ============================================================================
# EXAMPLE 2: Student-only endpoint
# ============================================================================
@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    """
    Create a new reservation - ONLY students can access.
    Teachers will receive: 403 Forbidden with code "not_student"
    """
    user = request.user
    activity_slot_id = request.data.get("activity_slot_id")
    note = request.data.get("note", "")
    
    try:
        activity_slot = ActivitySlot.objects.get(id=activity_slot_id)
    except ActivitySlot.DoesNotExist:
        return Response({
            "detail": "Activity slot not found.",
            "code": "slot_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if student already has reservation
    existing = Reservation.objects.filter(
        user=user,
        activity_slot=activity_slot
    ).exists()
    
    if existing:
        return Response({
            "detail": "You already have a reservation for this slot.",
            "code": "duplicate_reservation"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create reservation
    reservation = Reservation.objects.create(
        user=user,
        activity_slot=activity_slot,
        note=note,
        status=Reservation.Status.PENDING
    )
    
    serializer = ReservationSerializer(reservation)
    return Response({
        "detail": "Reservation created successfully.",
        "reservation": serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsStudent])
def get_my_reservations(request):
    """
    Get all reservations for the current student.
    Only students can access.
    """
    reservations = Reservation.objects.filter(user=request.user)
    serializer = ReservationSerializer(reservations, many=True)
    return Response({
        "reservations": serializer.data
    })


# ============================================================================
# EXAMPLE 3: Teacher-only endpoint
# ============================================================================
@api_view(["GET"])
@permission_classes([IsTeacher])
def get_all_reservations(request):
    """
    Get all reservations in the system - ONLY teachers can access.
    Students will receive: 403 Forbidden with code "not_teacher"
    """
    reservations = Reservation.objects.all().select_related('user', 'activity_slot__activity')
    serializer = ReservationSerializer(reservations, many=True)
    return Response({
        "reservations": serializer.data,
        "total_count": reservations.count()
    })


@api_view(["PATCH"])
@permission_classes([IsTeacher])
def approve_reservation(request, reservation_id):
    """
    Approve or reject a student reservation.
    Only teachers can approve/reject.
    """
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({
            "detail": "Reservation not found.",
            "code": "reservation_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get("action")  # "approve" or "cancel"
    
    if action == "approve":
        reservation.status = Reservation.Status.APPROVED
        message = "Reservation approved successfully."
    elif action == "cancel":
        reservation.status = Reservation.Status.CANCELLED
        message = "Reservation cancelled successfully."
    else:
        return Response({
            "detail": "Invalid action. Use 'approve' or 'cancel'.",
            "code": "invalid_action"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    reservation.save()
    serializer = ReservationSerializer(reservation)
    
    return Response({
        "detail": message,
        "reservation": serializer.data
    })


# ============================================================================
# EXAMPLE 4: Admin-only endpoint
# ============================================================================
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_activity(request):
    """
    Create a new activity - ONLY admins can access.
    Students and teachers will receive: 403 Forbidden with code "not_admin"
    """
    serializer = ActivitySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            "detail": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response({
        "detail": "Activity created successfully.",
        "activity": serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_activity(request, activity_id):
    """
    Delete an activity - ONLY admins can access.
    """
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({
            "detail": "Activity not found.",
            "code": "activity_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    activity.delete()
    return Response({
        "detail": "Activity deleted successfully."
    }, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# EXAMPLE 5: Teacher OR Admin endpoint
# ============================================================================
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def create_activity_slot(request):
    """
    Create a time slot for an activity.
    Both teachers and admins can create slots.
    Students will receive: 403 Forbidden with code "insufficient_permissions"
    """
    activity_id = request.data.get("activity_id")
    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    teacher_id = request.data.get("teacher_id")
    
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({
            "detail": "Activity not found.",
            "code": "activity_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create slot
    slot_data = {
        "activity": activity.id,
        "start_date": start_date,
        "end_date": end_date,
        "teacher": teacher_id
    }
    
    serializer = ActivitySlotSerializer(data=slot_data)
    
    if not serializer.is_valid():
        return Response({
            "detail": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response({
        "detail": "Activity slot created successfully.",
        "slot": serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsTeacherOrAdmin])
def get_reservation_statistics(request):
    """
    Get reservation statistics.
    Both teachers and admins can view statistics.
    """
    total_reservations = Reservation.objects.count()
    pending = Reservation.objects.filter(status=Reservation.Status.PENDING).count()
    approved = Reservation.objects.filter(status=Reservation.Status.APPROVED).count()
    cancelled = Reservation.objects.filter(status=Reservation.Status.CANCELLED).count()
    
    return Response({
        "statistics": {
            "total": total_reservations,
            "pending": pending,
            "approved": approved,
            "cancelled": cancelled
        }
    })


# ============================================================================
# EXAMPLE 6: Student OR Teacher endpoint
# ============================================================================
@api_view(["GET"])
@permission_classes([IsStudentOrTeacher])
def get_available_activities(request):
    """
    Get all available activities.
    Both students and teachers can view activities.
    Activities are filtered by user's role.
    """
    user = request.user
    
    # Filter activities based on user's role
    if user.role:
        activities = Activity.objects.filter(role=user.role)
    else:
        activities = Activity.objects.none()
    
    serializer = ActivitySerializer(activities, many=True)
    return Response({
        "activities": serializer.data,
        "count": activities.count()
    })


@api_view(["GET"])
@permission_classes([IsStudentOrTeacher])
def get_activity_slots(request, activity_id):
    """
    Get all time slots for a specific activity.
    Both students and teachers can view slots.
    """
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({
            "detail": "Activity not found.",
            "code": "activity_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify user has permission to see this activity (role check)
    if activity.role != request.user.role:
        return Response({
            "detail": "You don't have permission to view this activity.",
            "code": "insufficient_permissions"
        }, status=status.HTTP_403_FORBIDDEN)
    
    slots = ActivitySlot.objects.filter(activity=activity)
    serializer = ActivitySlotSerializer(slots, many=True)
    
    return Response({
        "activity": ActivitySerializer(activity).data,
        "slots": serializer.data,
        "count": slots.count()
    })


# ============================================================================
# EXAMPLE 7: Complex permission logic
# ============================================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticatedWithValidToken])
def update_reservation(request, reservation_id):
    """
    Update a reservation with custom permission logic.
    - Students can update their own reservations (note only)
    - Teachers can update any reservation (including status)
    - Token is always validated first
    """
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({
            "detail": "Reservation not found.",
            "code": "reservation_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    
    # Check permissions
    is_owner = reservation.user == user
    is_teacher = user.role and user.role.name.lower() == 'teacher'
    is_admin = user.role and user.role.name.lower() == 'admin'
    
    if not (is_owner or is_teacher or is_admin):
        return Response({
            "detail": "You don't have permission to update this reservation.",
            "code": "insufficient_permissions"
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Update reservation
    note = request.data.get("note")
    if note is not None:
        reservation.note = note
    
    # Only teachers and admins can change status
    status_update = request.data.get("status")
    if status_update:
        if not (is_teacher or is_admin):
            return Response({
                "detail": "Only teachers and admins can change reservation status.",
                "code": "insufficient_permissions"
            }, status=status.HTTP_403_FORBIDDEN)
        reservation.status = status_update
    
    reservation.save()
    serializer = ReservationSerializer(reservation)
    
    return Response({
        "detail": "Reservation updated successfully.",
        "reservation": serializer.data
    })
