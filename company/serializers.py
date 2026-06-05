from rest_framework import serializers
from .models import CompanyInfo, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'position', 'bio', 'email', 'phone',
            'linkedin', 'twitter', 'instagram', 'profile_image'
        ]


class CompanyInfoSerializer(serializers.ModelSerializer):
    team_members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyInfo
        fields = [
            'id', 'name', 'description', 'mission', 'vision', 'established_year',
            'email', 'phone', 'address', 'city', 'country',
            'website', 'facebook', 'instagram', 'twitter', 'linkedin',
            'logo', 'cover_image', 'team_members'
        ]
