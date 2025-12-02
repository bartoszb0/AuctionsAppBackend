from django.shortcuts import get_object_or_404
from .models import User, Auction, Bid
from rest_framework import generics
from .serializers import UserSerializer, AuctionSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.pagination import PageNumberPagination
from django.db.models import Max
from django.db.models.functions import Coalesce
from .filters import AuctionFilter

class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class RetrieveUserAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_url_kwarg = 'user_id'
    permission_classes = [AllowAny]


class ListCreateAuctionAPIView(generics.ListCreateAPIView):
    serializer_class = AuctionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = AuctionFilter
    search_fields = ['name']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 20
    ordering_fields = ['created_on', 'highest_bid_amount', 'deadline']

    def get_queryset(self):
        queryset = Auction.objects.all().annotate(
            highest_bid_amount=Coalesce(Max('bids__amount'), 'starting_price')
        ).order_by('-created_on')

        is_closed_filter = self.request.query_params.get('closed', 'false')

        if is_closed_filter.lower() == 'true':
            return queryset.filter(closed=True)
        else:
            return queryset.filter(closed=False)

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


class ListCreateBidAPIView(generics.ListCreateAPIView):
    queryset = Bid.objects.all() 
    serializer_class = BidSerializer
    lookup_url_kwarg = 'auction_id'
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        auction = get_object_or_404(Auction, pk=self.kwargs.get(self.lookup_url_kwarg))
        queryset = queryset.filter(auction=auction)
        return queryset.order_by('-amount')
    
    def perform_create(self, serializer):
        auction_id = self.kwargs.get(self.lookup_url_kwarg)
        auction = get_object_or_404(Auction, pk=auction_id)
        serializer.save(bidder=self.request.user, auction=auction)

