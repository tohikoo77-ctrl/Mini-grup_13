from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import models
from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """Create and view feedback"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Allow any for create, authenticated for list/detail"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['list', 'my_feedback']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Users see only their own feedback"""
        if self.request.user.is_authenticated:
            return Feedback.objects.filter(user=self.request.user)
        return Feedback.objects.none()

    def create(self, request, *args, **kwargs):
        """Create new feedback"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_feedback(self, request):
        """Get current user's feedback"""
        feedbacks = Feedback.objects.filter(user=request.user)
        serializer = self.get_serializer(feedbacks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get feedback statistics"""
        total = Feedback.objects.count()
        by_category = {}
        for choice in Feedback.CATEGORY_CHOICES:
            count = Feedback.objects.filter(category=choice[0]).count()
            by_category[choice[0]] = count

        avg_rating = Feedback.objects.values('rating').aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0

        return Response({
            'total_feedback': total,
            'by_category': by_category,
            'average_rating': round(float(avg_rating), 2)
        })
