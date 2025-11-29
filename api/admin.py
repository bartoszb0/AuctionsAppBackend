from django.contrib import admin
from .models import Auction, User, AuctionImage, Bid

# Register your models here.
admin.site.register(Auction)
admin.site.register(User)
admin.site.register(AuctionImage)
admin.site.register(Bid)