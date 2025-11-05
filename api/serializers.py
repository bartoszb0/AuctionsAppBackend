from .models import User, Auction
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class AuctionSerializer(serializers.ModelSerializer):
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