from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ai import PLATFORM_LIMITS, generate_social_post
from .serializers import GeneratePostSerializer


def generate_post_page(request):
    platforms = list(PLATFORM_LIMITS.keys())
    result = None
    error = None
    topic = ""
    platform = platforms[0]

    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        platform = request.POST.get("platform", platforms[0])
        if topic and platform in PLATFORM_LIMITS:
            try:
                result = generate_social_post(topic, platform)
            except Exception:
                error = "Post generation failed. Check your API key and try again."

    return render(request, "social_media/generate.html", {
        "platforms": platforms,
        "result": result,
        "error": error,
        "topic": topic,
        "platform": platform,
    })


class GeneratePostView(APIView):
    def post(self, request):
        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        topic = serializer.validated_data["topic"]
        platform = serializer.validated_data["platform"]

        try:
            result = generate_social_post(topic, platform)
        except Exception:
            return Response(
                {"error": "Post generation failed. Check your API key and try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({
            "platform": platform,
            "content": result.content,
            "hashtags": result.hashtags,
            "character_count": result.character_count,
        })
