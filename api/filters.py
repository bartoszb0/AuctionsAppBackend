import django_filters # type: ignore
from .models import Auction

class AuctionFilter(django_filters.FilterSet):
    min_bid = django_filters.NumberFilter(field_name='highest_bid_amount', lookup_expr='gte')
    max_bid = django_filters.NumberFilter(field_name='highest_bid_amount', lookup_expr='lte')

    class Meta:
        model = Auction
        fields = ['category', 'min_bid', 'max_bid',]
