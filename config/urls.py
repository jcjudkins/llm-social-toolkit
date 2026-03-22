from django.urls import path, include

from social_media.views import generate_post_page

urlpatterns = [
    path("", generate_post_page, name="generate"),
    path("api/", include("social_media.urls")),
]
