from django.db import models
from accounts.models import Role
from django.conf import settings


class Activity(models.Model):
    name = models.CharField(max_length=150, blank=False)
    description = models.TextField()
    capacity = models.IntegerField(blank=False)
    available_hours = models.CharField(max_length=200, help_text="Dostupné hodiny aktivity, napr. 7:30-16:00.")
    color = models.CharField(max_length=150, default="#778899", help_text="Farba aktivity pre zobrazenie v kalendári(hex kód).")
    category = models.CharField(max_length=100, null=True)
    room = models.CharField(max_length=20, help_text="Miestnosť alebo miesto konania aktivity.")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, help_text="Rola, ktorá môže participovať na aktivite(napr ucitel nevidi" \
    " ps5 rezervaciu a student nevidi rezervaciu triedy).")

    def __str__(self):
        return self.name
    

class ActivitySlot(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, help_text="Učiteľ priradený k slotu (hlavne kvoli" \
    " konzultaciam, môže byť null).")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.activity.name
    

class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Čaká sa"
        CANCELLED = "cancelled", "Zrušené"
        APPROVED = "approved", "Schválené"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_slot = models.ForeignKey(ActivitySlot, on_delete=models.CASCADE)
    note = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=Status.choices)

    def __str__(self):
        return self.user.username
