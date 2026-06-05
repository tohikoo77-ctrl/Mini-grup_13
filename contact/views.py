from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from .models import ContactMessage, MessageReply
from .serializers import ContactMessageSerializer, MessageReplySerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    """Send contact messages and manage conversations"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Allow any for create, authenticated for most actions"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['list', 'admin_list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Users see only their own messages"""
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        elif self.request.user.is_authenticated:
            return ContactMessage.objects.filter(user=self.request.user)
        return ContactMessage.objects.none()

    def create(self, request, *args, **kwargs):
        """Create new contact message"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_messages(self, request):
        """Get current user's contact messages"""
        messages = ContactMessage.objects.filter(user=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_list(self, request):
        """Get all messages for admin"""
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        
        queryset = ContactMessage.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_reply(self, request, pk=None):
        """Add reply to contact message"""
        message = self.get_object()
        serializer = MessageReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(message=message, sender=request.user)
            message.status = 'open'
            message.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def change_status(self, request, pk=None):
        """Change message status"""
        message = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(ContactMessage.STATUS_CHOICES):
            message.status = new_status
            if new_status == 'resolved':
                message.resolved_at = timezone.now()
            message.save()
            return Response({'status': 'Status changed'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_to(self, request, pk=None):
        """Assign message to staff member"""
        message = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        try:
            from django.conf import settings
            User = settings.AUTH_USER_MODEL
            from user.models import User as UserModel
            staff = UserModel.objects.get(id=assigned_to_id, is_staff=True)
            message.assigned_to = staff
            message.save()
            serializer = self.get_serializer(message)
            return Response(serializer.data)
        except Exception:
            return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
