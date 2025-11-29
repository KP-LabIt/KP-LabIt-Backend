from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Activity, ActivitySlot, Reservation
from .serializer import ActivitySerializer, ActivitySlotSerializer, ReservationSerializer

# view pre vseobecne api veci ako aktivity, rezervacie atd(keby bol v tom chaos, tak sa vie popripadne spravit pre kazdu vec vlastna appka
# napr. že už mame pre accounts appku, tak vieme spraviť aj čisto pre rezervacie, a potom pre aktivity...)



@api_view(["GET"])
def get_init(request):
    return Response("Endpoint pre api...")

