from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role

# registrovanie custom usera, aby v admin paneli mohol admin vidieť a upravovat usera + role

class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("username", "email", "role", "is_staff", "is_superuser")

    fieldsets = UserAdmin.fieldsets + (
        ("Custom fields", {"fields": ("role",)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
