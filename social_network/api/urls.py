from django.urls import path
from .views import UserSignupView, UserLoginView, UserSearchView, FriendRequestView, FriendListView, PendingFriendRequestListView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('pending-requests/', PendingFriendRequestListView.as_view(), name='pending_requests'),
]
