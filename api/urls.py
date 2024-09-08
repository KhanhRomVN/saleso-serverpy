from django.urls import path
from . import views

urlpatterns = [
    path('recommend/<str:product_id>/', views.get_recommendations, name='get_recommendations'),
]