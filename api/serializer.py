from rest_framework import serializers
from unicodedata import category

from .models import Activity, ActivitySlot, Reservation


# na konvertnutie json dat do django modelu a naopak cca

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"

class ActivitySlotSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = ActivitySlot
        fields = ["id", "start_date", "end_date", "activity", "teacher"]

    def get_teacher(self, obj):
        teacher = obj.teacher
        if not teacher:
            return None
        return {
            "id": teacher.id,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name,
        }


class ReservationSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    activity_slot = ActivitySlotSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user",
            "activity_slot",
            "note",
            "created_at",
            "status",
            "status_label",
        ]
        read_only_fields = ["id", "created_at"]

    def get_status_label(self, obj):
        return obj.get_status_display()

    def get_user(self, obj):
        request = self.context.get("request")
        requester = request.user if request else None

        # ak request poslal učiteľ, zobraz študenta
        if requester and requester.role and requester.role.name == "teacher":
            target_user = obj.user
        else:
            target_user = requester

        if not target_user:
            return None

        return {
            "id": target_user.id,
            "email": target_user.email,
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "role": target_user.role.name if target_user.role else None,
        }

# Serializer pre checknutie validacie dát pre časť z aktivity_slot
class ActivitySlotCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitySlot
        fields = ["id", "start_date", "end_date"]  # leave out activity and teacher

# Serializer pre validáciu a ukladanie aktivít spolu s akitivty slotmi
class ActivityWithSlotsSerializer(serializers.ModelSerializer):
    activity_slots = ActivitySlotCheckSerializer(many=True)

    class Meta:
        model = Activity
        fields = ["name", "description", "capacity", "available_hours", "color", "category", "room", "role", "image_key", "activity_slots" ]

    def create(self, validated_data):
        slots_data = validated_data.pop("activity_slots")  # remove slots from main data
        request = self.context.get("request")  # we’ll use this to get teacher
        teacher = request.user  # teacher for all slots

        # Step 1: create the Activity
        activity = Activity.objects.create(**validated_data)

        # Step 2: create all ActivitySlots linked to the Activity and teacher
        for slot_data in slots_data:
            ActivitySlot.objects.create(
                activity=activity,
                teacher=teacher,  # assign teacher automatically
                **slot_data
            )

        return activity

