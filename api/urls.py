from django.urls import path

from . import views

urlpatterns = [
    path('auctions/', views.ListCreateAuctionAPIView.as_view(), name="auctions"),

]