from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Activity, ActivitySlot, Reservation

# registracia modelov, aby sa dali spravovat cez django admin panel

class ActivityAdmin(ModelAdmin):
    model = Activity
    list_display = ("name", "description", "capacity", "room", "category", "role", "color")
    search_fields = ("name", "description", "room", "category")
    list_filter = ("role", "category")

class ActivitySlotAdmin(ModelAdmin):
    model = ActivitySlot
    list_display = ("activity", "teacher", "start_date", "end_date")
    search_fields = ("activity__name", "teacher__username")
class ReservationAdmin(ModelAdmin):
    model = Reservation
    list_display = ("user", "activity_slot__activity", "status", "created_at", "activity_slot__start_date", "activity_slot__end_date")
    search_fields = ("user__username", "activity_slot__activity__name")
    list_filter = ("status", "activity_slot__activity")


admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivitySlot, ActivitySlotAdmin)
admin.site.register(Reservation, ReservationAdmin)

