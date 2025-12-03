from django.urls import path

from . import views

urlpatterns = [
    path('users/<int:user_id>/', views.RetrieveUserAPIView.as_view(), name="user"),
    path('users/<int:pk>/follow/', views.FollowUserView.as_view(), name="follow_user"),
    path('auctions/', views.ListCreateAuctionAPIView.as_view(), name="auctions"),
    path('auctions/<int:auction_id>/', views.RetrieveAuctionAPIView.as_view(), name="auction"),
    path('auctions/<int:auction_id>/bids/', views.ListCreateBidAPIView.as_view(), name="bids"),
    path('auctions/followed/', views.ListFollowedAuctionsAPIView.as_view(), name="followed_auctions")
]