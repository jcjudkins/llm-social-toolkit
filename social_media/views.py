from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ai import generate_social_post
from .serializers import GeneratePostSerializer


class GeneratePostView(APIView):
    def post(self, request):
        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        topic = serializer.validated_data["topic"]
        platform = serializer.validated_data["platform"]

        content = generate_social_post(topic, platform)
        return Response({"content": content, "platform": platform})
