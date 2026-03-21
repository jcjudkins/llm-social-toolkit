from django.urls import path
from .views import GeneratePostView

urlpatterns = [
    path("generate-post/", GeneratePostView.as_view()),
]
