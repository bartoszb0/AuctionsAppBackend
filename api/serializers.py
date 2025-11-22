from .models import User, Auction
from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class AuctionSerializer(serializers.ModelSerializer):
    highest_bid = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = [
            "id",
            "name",
            "description",
            "author",
            "starting_price",
            "minimal_bid",
            "created_on",
            "closed",
            "category",
            "deadline",
            "highest_bid",
        ]
        read_only_fields = ('author', 'highest_bid', 'created_on')

    def get_highest_bid(self, obj):
        value = getattr(obj, 'highest_bid_amount', None)
        if value is None:
            highest = obj.bids.order_by('-amount').first()
            value = highest.amount if highest else obj.starting_price
        value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return str(value)