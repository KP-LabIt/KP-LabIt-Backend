from django.db import models
from django.contrib.auth.models import AbstractUser





class Role(models.Model):
    name = models.CharField(max_length=100, blank=False, default='student', unique=True)
    description = models.TextField(blank=False)

    def __str__(self):
        return self.name

def get_default_role():
    return Role.objects.get(name="student")

class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=get_default_role)
    email = models.EmailField(blank=False, unique=True)

    must_change_password = models.BooleanField(default=True, help_text="User must change password on first login.")

    REQUIRED_FIELDS = ["email"]


    def __str__(self):
        return self.username


