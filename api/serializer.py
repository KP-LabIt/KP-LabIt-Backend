from rest_framework import serializers
from .models import Activity, ActivitySlot, Reservation


# na konvertnutie json dat do django modelu a naopak cca

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"

class ActivitySlotSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()
    class Meta:
        model = ActivitySlot
        fields = ["id", "start_date", "end_date", "activity", "teacher"]


class ReservationSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    activity_slot = ActivitySlotSerializer()

    class Meta:
        model = Reservation
        fields = ["id", "user", "activity_slot", "note", "created_at", "status", "status_label"]
        read_only_fields = ["id", "created_at"]

    def get_status_label(self, obj):
        return obj.get_status_display()
