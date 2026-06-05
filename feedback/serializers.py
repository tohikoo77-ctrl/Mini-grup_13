from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True, allow_blank=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'category', 'rating', 'title', 'message', 'email', 'name',
            'phone', 'user', 'user_name', 'is_read', 'is_resolved',
            'admin_response', 'attachments', 'created_at'
        ]
        read_only_fields = ['id', 'is_read', 'is_resolved', 'admin_response', 'created_at', 'user']

    def create(self, validated_data):
        """Automatically set user if authenticated"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
