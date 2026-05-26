from django.urls import path
from rest_framework.routers import DefaultRouter

from .news_views import NewsViewSet
from .views import (
    HomeView,
    OrderAddressViewSet,
    OrderReviewViewSet,
    ProductCompareView,
    ProductComparisonViewSet,
    ProductDiscoveryView,
    UserOrdersView,
    UserProfileView,
)

router = DefaultRouter()
router.register("news", NewsViewSet, basename="news")
router.register("order-addresses", OrderAddressViewSet, basename="order-addresses")
router.register("order-reviews", OrderReviewViewSet, basename="order-reviews")
router.register("product-comparisons", ProductComparisonViewSet, basename="product-comparisons")

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("products/", ProductDiscoveryView.as_view(), name="products-discovery"),
    path("products/compare/", ProductCompareView.as_view(), name="products-compare"),
    path("me/orders/", UserOrdersView.as_view(), name="user-orders"),
    path("me/profile/", UserProfileView.as_view(), name="user-profile"),
    *router.urls,
]
