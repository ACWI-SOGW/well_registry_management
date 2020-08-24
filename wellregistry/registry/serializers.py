"""
Serializers for the REST API
"""

from rest_framework.serializers import ModelSerializer

from .models import Registry

class RegistrySerializer(ModelSerializer):
    class Meta:
        model = Registry
        fields = '__all__'