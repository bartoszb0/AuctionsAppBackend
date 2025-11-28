from django.contrib import admin
from .models import Auction, User, AuctionImage

# Register your models here.
admin.site.register(Auction)
admin.site.register(User)
admin.site.register(AuctionImage)