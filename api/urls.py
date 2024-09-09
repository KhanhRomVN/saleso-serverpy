from django.urls import path
from .views import HelloWorldAPIView

urlpatterns = [
    path('', HelloWorldAPIView.as_view(), name='hello-world-api'),
]