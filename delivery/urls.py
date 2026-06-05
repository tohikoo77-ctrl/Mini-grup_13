from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingMethodViewSet, OrderTrackingViewSet

router = DefaultRouter()
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-method')
router.register(r'tracking', OrderTrackingViewSet, basename='tracking')

urlpatterns = [
    path('', include(router.urls)),
]
