from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CompanyInfo, TeamMember
from .serializers import CompanyInfoSerializer, TeamMemberSerializer


class CompanyInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """Get company information"""
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = []

    @action(detail=False, methods=['get'])
    def main(self, request):
        """Get main company info"""
        company = CompanyInfo.objects.first()
        if company:
            serializer = self.get_serializer(company)
            return Response(serializer.data)
        return Response({'detail': 'Company info not found'})


class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """Get team members"""
    serializer_class = TeamMemberSerializer
    permission_classes = []

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('order', 'name')

    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """Filter team members by position"""
        position = request.query_params.get('position')
        if position:
            queryset = self.get_queryset().filter(position=position)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
