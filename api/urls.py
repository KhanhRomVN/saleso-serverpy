from django.urls import path
from . import views

urlpatterns = [
    path('update-and-train-product-recommend', views.updateAndTrainProductRecommend, name='update_and_train_product_recommend'),
    path('recommend-product/<str:id>/', views.get_recommendations, name='get_recommendations'),
]
