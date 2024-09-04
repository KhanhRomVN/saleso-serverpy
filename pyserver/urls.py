from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import RegisterView, LoginView
from product.views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
]