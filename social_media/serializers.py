from rest_framework import serializers
from .ai import PLATFORM_LIMITS


class GeneratePostSerializer(serializers.Serializer):
    topic = serializers.CharField(min_length=1, max_length=512)
    platform = serializers.ChoiceField(choices=list(PLATFORM_LIMITS.keys()))
