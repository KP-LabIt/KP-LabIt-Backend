from rest_framework import serializers
from .models import Test

# na konvertnutie json dat do django modelu a naopak cca

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"