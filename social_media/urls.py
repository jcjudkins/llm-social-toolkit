from django.urls import path

from .views import GeneratePostView, task_status

urlpatterns = [
    path("generate-post/", GeneratePostView.as_view()),
    path("task/<str:task_id>/", task_status),
]
