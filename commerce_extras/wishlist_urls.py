from rest_framework.routers import DefaultRouter

from .wishlist_views import WishlistViewSet

router = DefaultRouter()
router.register(r"", WishlistViewSet, basename="wishlist")

urlpatterns = router.urls
