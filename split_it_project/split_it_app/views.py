from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics
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

class UserApi(APIView):
    """ List all the users in the application. """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """ Return a list of all users. """
        
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    """ Registers a new user in the application. """
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginApi(APIView):
    """ Logs in a registered user after authentication in the application. """
    serializer = LoginSerializer
    
    def post(self, request):
        """ Authenticate and logs in a user. """
        
        data = request.data
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.data['username']
        password = serializer.data['password']
            
        user = authenticate(username=username, password=password)
        if user is not None:
            return Response(get_tokens_for_user(), status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'Invalid Credentials'}, status.HTTP_401_UNAUTHORIZED)            