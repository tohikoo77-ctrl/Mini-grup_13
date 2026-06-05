from rest_framework import serializers
from .models import ContactMessage, MessageReply


class MessageReplySerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name', read_only=True)

    class Meta:
        model = MessageReply
        fields = ['id', 'sender', 'sender_name', 'content', 'is_internal', 'attachments', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    replies = MessageReplySerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.first_name', read_only=True, allow_blank=True)

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'subject', 'message', 'sender_name', 'sender_email', 'sender_phone',
            'user', 'user_name', 'status', 'priority', 'assigned_to',
            'replies', 'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'status', 'assigned_to', 'created_at', 'updated_at', 'resolved_at', 'user']

    def create(self, validated_data):
        """Automatically set user if authenticated"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
