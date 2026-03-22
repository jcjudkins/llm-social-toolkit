from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ai import PLATFORM_LIMITS, ProviderNotConfiguredError, generate_social_post
from .serializers import GeneratePostSerializer
from .tasks import generate_post_task


def generate_post_page(request):
    platforms = list(PLATFORM_LIMITS.keys())
    task_id = None
    topic = ""
    platform = platforms[0]

    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        platform = request.POST.get("platform", platforms[0])
        if topic and platform in PLATFORM_LIMITS:
            task = generate_post_task.delay(topic, platform)
            task_id = task.id

    return render(request, "social_media/generate.html", {
        "platforms": platforms,
        "task_id": task_id,
        "topic": topic,
        "platform": platform,
    })


def task_status(request, task_id):
    result = AsyncResult(task_id)
    if result.state == "SUCCESS":
        return JsonResponse({"status": "SUCCESS", "result": result.get()})
    if result.state == "FAILURE":
        return JsonResponse({"status": "FAILURE", "error": str(result.result)})
    return JsonResponse({"status": result.state})


class GeneratePostView(APIView):
    def post(self, request):
        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        topic = serializer.validated_data["topic"]
        platform = serializer.validated_data["platform"]

        try:
            result = generate_social_post(topic, platform)
        except ProviderNotConfiguredError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
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
