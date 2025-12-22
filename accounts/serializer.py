from rest_framework import serializers
from .models import User, Role

# na konvertnutie json dat do django modelu a naopak cca

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role", "date_joined"]
        read_only_fields = ["id", "date_joined"]