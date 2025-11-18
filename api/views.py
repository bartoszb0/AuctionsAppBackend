from .models import User, Auction
from rest_framework import generics
from .serializers import UserSerializer, AuctionSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend # type: ignore


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ListCreateAuctionAPIView(generics.ListCreateAPIView):
    queryset = Auction.objects.all().order_by('-created_on')
    serializer_class = AuctionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class RetrieveAuctionAPIView(generics.RetrieveAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    lookup_url_kwarg = 'auction_id'
    permission_classes = [AllowAny]