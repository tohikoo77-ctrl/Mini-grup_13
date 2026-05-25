from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    ChangeUsernameView,
    HomeView,
    NewsViewSet,
    OrderAddressViewSet,
    OrderReviewViewSet,
    ProductCompareView,
    ProductComparisonViewSet,
    ProductDiscoveryView,
    UserOrdersView,
    UserProfileView,
    WishlistViewSet,
)

router = DefaultRouter()
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("news", NewsViewSet, basename="news")
router.register("order-addresses", OrderAddressViewSet, basename="order-addresses")
router.register("order-reviews", OrderReviewViewSet, basename="order-reviews")
router.register("product-comparisons", ProductComparisonViewSet, basename="product-comparisons")

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("homepage/", HomeView.as_view(), name="homepage"),
    path("products/", ProductDiscoveryView.as_view(), name="products-discovery"),
    path("products/list/", ProductDiscoveryView.as_view(), name="products-list"),
    path("products/compare/", ProductCompareView.as_view(), name="products-compare"),
    path("product-compare/", ProductCompareView.as_view(), name="product-compare"),
    path("me/orders/", UserOrdersView.as_view(), name="user-orders"),
    path("me/profile/", UserProfileView.as_view(), name="user-profile"),
    path("me/password/", ChangePasswordView.as_view(), name="user-password"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("me/username/", ChangeUsernameView.as_view(), name="user-username"),
    path("change-username/", ChangeUsernameView.as_view(), name="change-username"),
    *router.urls,
]
