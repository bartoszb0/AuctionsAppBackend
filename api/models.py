from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Auction(models.Model):
    class CategoryChoices(models.TextChoices):
        HOME = 'Home'
        SPORTS = 'Sports'
        MUSIC = 'Music'
        ELECTRONICS = 'Electronics'
        CLOTHING = 'Clothing'
        OTHER = 'Other'

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    starting_price = models.DecimalField(max_digits=9, decimal_places=2)
    minimal_bid = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    category = models.CharField(max_length=11, choices=CategoryChoices.choices)
    deadline = models.DateTimeField()

    @property
    def highest_bid(self):
        highest = self.bids.order_by('-amount').first()
        return highest.amount if highest else self.starting_price

class Bid(models.Model):
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
