from .models import AuctionImage, User, Auction, Bid
from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP


    

class AuctionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionImage
        fields = ['id', 'image']

    
class AuctionSerializer(serializers.ModelSerializer):
    highest_bid = serializers.SerializerMethodField()
    images = AuctionImageSerializer(many=True, read_only=True)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
    )

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
            "images",
            "uploaded_images"
        ]
        read_only_fields = ('author', 'highest_bid', 'created_on')


    def validate_uploaded_images(self, images):
        if not images:
            raise serializers.ValidationError("At least one image is required.")

        if len(images) > 10:
            raise serializers.ValidationError("Max 10 images allowed.")

        for img in images:
            if img.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(f"{img.name} is too large (max 5MB).")

        return images


    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        auction = super().create(validated_data)

        for img in uploaded_images:
            AuctionImage.objects.create(auction=auction, image=img)

        return auction


    def get_highest_bid(self, obj):
        value = getattr(obj, 'highest_bid_amount', None)
        if value is None:
            highest = obj.bids.order_by('-amount').first()
            value = highest.amount if highest else obj.starting_price
        value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return str(value)


class UserSerializer(serializers.ModelSerializer):
    auctions = AuctionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "auctions"]
        extra_kwargs = {"password": {"write_only": True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class BidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'bidder', 'amount', 'placed_on']
