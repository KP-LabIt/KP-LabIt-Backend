from django.urls import path
from .views import get_init, get_user_reservations, delete_reservation

urlpatterns = [
    path("", get_init, name="get_init"),
    path("reservations/", get_user_reservations, name="get_user_reservations"),
    path("reservations/delete/<int:reservation_id>/", delete_reservation, name="delete_reservation"),
]