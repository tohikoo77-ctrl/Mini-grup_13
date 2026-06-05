from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactMessageViewSet

router = DefaultRouter()
router.register(r'', ContactMessageViewSet, basename='contact-message')

urlpatterns = [
    path('', include(router.urls)),
]
