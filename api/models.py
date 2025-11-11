from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    pass

class Auction(models.Model):
    class CategoryChoices(models.TextChoices):
        HOME = 'home'
        SPORTS = 'sports'
        MUSIC = 'music'
        ELECTRONICS = 'electronics'
        CLOTHING = 'clothing'
        OTHER = 'other'

    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    starting_price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal(0.01))])
    minimal_bid = models.DecimalField(max_digits=9, decimal_places=2, default=1.00, validators=[MinValueValidator(Decimal(0.01))])
    created_on = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    category = models.CharField(max_length=11, choices=CategoryChoices.choices)
    deadline = models.DateTimeField()

    @property
    def highest_bid(self):
        highest = self.bids.order_by('-amount').first()
        value = highest.amount if highest else self.starting_price
        return str(value)

class Bid(models.Model):
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="bids"
    )
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
