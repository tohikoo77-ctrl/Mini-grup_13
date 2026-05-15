from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')
router.register(r'items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('', include(router.urls)),
]