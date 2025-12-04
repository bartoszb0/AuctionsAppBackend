from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import AuctionImage, User, Auction, Bid
from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer    

class AuctionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionImage
        fields = ['id', 'image']


class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

    
class AuctionSerializer(serializers.ModelSerializer):
    highest_bid = serializers.SerializerMethodField()
    images = AuctionImageSerializer(many=True, read_only=True)
    author = SmallUserSerializer(read_only=True)

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
        read_only_fields = ('highest_bid', 'created_on')


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
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    auctions_count = serializers.IntegerField(source="auctions.count")
    open_auctions_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "password", "followers", "following", "auctions_count", "open_auctions_count"]
        extra_kwargs = {"password": {"write_only": True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def get_followers(self, obj):
        return SmallUserSerializer(obj.followers.all(), many=True).data
    
    def get_following(self, obj):
        return SmallUserSerializer(obj.follows.all(), many=True).data
    
    def get_open_auctions_count(self, obj):
        return obj.auctions.filter(closed=False).count()
    
class BidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'bidder', 'amount', 'placed_on']
        read_only_fields = ['auction']
        
    def validate(self, attrs):
        request = self.context['request']
        view = self.context['view']
        auction_id = view.kwargs.get('auction_id')

        auction = get_object_or_404(Auction, pk=auction_id)
        amount = attrs['amount']
        user = request.user

        if user == auction.author:
            raise serializers.ValidationError("You can't bid on your auction")
        
        if auction.deadline < timezone.now():
            raise serializers.ValidationError("Auction has ended")
        

        highest_bid = auction.bids.order_by('-amount').first()
        highest_amount = Decimal(highest_bid.amount) if highest_bid else Decimal('0')

        minimal_allowed = Decimal(auction.minimal_bid) + highest_amount

        if Decimal(amount) < minimal_allowed:
            raise serializers.ValidationError(f"Bid must be at least ${minimal_allowed}")

        return attrs


# Ensuring the new bid is higher than the last bid.
# Ensuring a user can't bid on their own auction.
# Checking if the auction is still open (not expired).

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
