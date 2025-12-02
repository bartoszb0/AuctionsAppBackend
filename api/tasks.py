from celery import shared_task
from django.utils import timezone
from .models import Auction

@shared_task
def close_expired_auctions():
    now = timezone.now()
    expired = Auction.objects.filter(closed=False, deadline__lte=now)
    expired.update(closed=True)
    print(f"Closed {expired.count()} auctions")