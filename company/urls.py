from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyInfoViewSet, TeamMemberViewSet

router = DefaultRouter()
router.register(r'info', CompanyInfoViewSet, basename='company-info')
router.register(r'team', TeamMemberViewSet, basename='team-member')

urlpatterns = [
    path('', include(router.urls)),
]
