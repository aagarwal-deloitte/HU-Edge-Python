from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, OccasionSerializer, EventSerializer
from .models import Occasion, Event
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Generates Token
def get_tokens_for_user(user):
    """ It generates access token for the registered user. """
    
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserApi(generics.GenericAPIView):
    """ List all the users in the application. """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request):
        """ Return a list of all users. """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterApi(generics.CreateAPIView):
    """ Registers a new user in the application. """
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginApi(generics.GenericAPIView):
    """ Logs in a registered user after authentication in the application. """
    
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    
    def post(self, request):
        """ Authenticate and logs in a user. """
        
        data = request.data
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
            
        user = authenticate(username=username, password=password)
        if user is not None:
            return Response(get_tokens_for_user(user), status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'Invalid Credentials'}, status.HTTP_401_UNAUTHORIZED)
                   
class OccasionApi(generics.ListCreateAPIView):
    """ Allows the user to create and view the occasion. """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OccasionSerializer 
    
    def get_queryset(self):
        return Occasion.objects.filter(created_by=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)  
        
class EventApi(generics.ListCreateAPIView):
    """ Allows the user to create and view the event and tag it to occasion (optional). """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class =  EventSerializer 
    
    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
class ExpenseApi(APIView):
    """ Allows the user to clear the expense. """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None
    
    def post(self, request):
        user_name = request.data.get('user')
        event_name = request.data.get('event')
        split_amount = request.data.get('amount')
        
        if not user_name or not event_name:
            return Response({'message': 'User and Event are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event = Event.objects.get(description=event_name)
        except Event.DoesNotExist:
            return Response({'message': 'Provided event does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        if event.clear_expense(user_name, split_amount):
            return Response({
            "message": f'Updated expense for user: {user_name} for event: {event_name}.',
            "updated_expense": event.expense_split
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            "message": f'No such user: {user_name} found for event: {event_name}.',
            "updated_expense": event.expense_split
        }, status=status.HTTP_404_NOT_FOUND)
            
class OccasionSummaryApi(APIView):
    """ Allows the user to view the summary of the occasion. """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None
    
    def get(self, request, pk, format=None):
        occasion = Occasion.objects.get(pk=pk)
        expenditure_summary = occasion.get_expenditure_summary()
        return Response(expenditure_summary, status=status.HTTP_200_OK)