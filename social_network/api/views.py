from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User, FriendRequest, Friendship 
from .serializers import UserSerializer, FriendRequestSerializer
from .constants import *
from .throttles import FriendRequestThrottle


class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        name = request.data.get('name')

        if not email or not password or not name:
            return Response({'error': 'Email, password, and name are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email ID already exists, please try logging in.'}, status=status.HTTP_200_OK )

        user = User.objects.create_user(email=email, password=password, name=name)
        print(f"User created with email: {user.email} and password {user.password}")  # Debug statement
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        print(f"Attempting to authenticate user with email: {email} and password: {password}")  # Debug statement
        
        user = authenticate(request, username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})
        print("Authentication failed")  # Debug statement
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', '').lower()
        
        if '@' in keyword:
            # Search by exact email match
            queryset = User.objects.filter(email__iexact=keyword)
        else:
            # Search by name containing the keyword
            queryset = User.objects.filter(name__icontains=keyword)
        
        return queryset.order_by('id')


class FriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_throttles(self):        
        if self.request.method == 'POST':
            return [FriendRequestThrottle()]
        return []
    
    def put(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        friend_request_status = request.data.get('friend_request_status')
        print("in put friend request")
        if not request_id or not status:    
            return Response({'error': 'request_id and status are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.status == ACCEPTED:    
            return Response({'info': 'Friend request already accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.status = friend_request_status
        friend_request.save()
        
        if friend_request_status == ACCEPTED:
            # Create the reciprocal friendship
            Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
            Friendship.objects.create(user1=friend_request.to_user, user2=friend_request.from_user)

        return Response(FriendRequestSerializer(friend_request).data)

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({'error': 'to_user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        to_user = User.objects.get(id=to_user_id)

        # Check the number of friend requests sent in the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            from_user=request.user, 
            timestamp__gte=one_minute_ago
        ).count()

        if recent_requests_count >= 3:
            return Response({'error': 'You can only send 3 friend requests per minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Check if there's an existing friend request
        existing_request = FriendRequest.objects.filter(from_user=request.user, to_user=to_user).first()
        if existing_request:
            if existing_request.status == PENDING:
                return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_request.status == REJECTED:
                # Update the existing request's status to pending
                existing_request.status = PENDING
                existing_request.save()
                return Response(FriendRequestSerializer(existing_request).data, status=status.HTTP_200_OK)
        
        friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)


class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        friendships = Friendship.objects.filter(user1=self.request.user)
        friend_ids = [friendship.user2.id for friendship in friendships]
        
        queryset = User.objects.filter(id__in=friend_ids)
        return queryset.order_by('id') 


class PendingFriendRequestListView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = FriendRequest.objects.filter(to_user=self.request.user, status='pending')
        return queryset.order_by('id') 
        
