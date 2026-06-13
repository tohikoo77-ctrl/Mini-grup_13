from django.urls import path
from .views import FAQListAPIView

urlpatterns = [
    path("", FAQListAPIView.as_view(), name="faq-list"),
]
