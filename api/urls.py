from django.urls import path
from .views import get_init, get_user_reservations, change_reservation_status, delete_reservation, get_activities, create_activity

urlpatterns = [
    path("", get_init, name="get_init"),
    path("reservations/", get_user_reservations, name="get_user_reservations"),
    path("reservations/change_status/<int:reservation_id>/", change_reservation_status, name="change_reservation_status"),
    path("reservations/delete/<int:reservation_id>/", delete_reservation, name="delete_reservation"),
    path("activities/", get_activities, name="get_activities"),
    path("activities/create/", create_activity, name="create_activity"),
]