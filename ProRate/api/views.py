from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from .models import Rating
from .serializers import RatingSerializer


from .models import Professor, Module, Rating
from .serializers import ProfessorSerializer, ModuleSerializer, RatingSerializer, UserSerializer

# Create your views here.

@ensure_csrf_cookie
def home(request):
    return HttpResponse("CSRF token set")

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data["password"])
        user.save()
        return Response({"message": "You Have Been Registered"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):

    #Authenticating User, making sure that user exists, if user exists "user' will be true
    user = authenticate(username=request.data['username'], password=request.data['password'])

    if user:
        login(request, user)
        return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    if not request.user.is_authenticated:
        return Response({"message": "You are not logged in."}, status=status.HTTP_200_OK)
    logout(request)
    return Response({"message": "You have been logged out."}, status=status.HTTP_200_OK)

#ReadOnly API endpoint 
class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer

    def get_queryset(self):
        return Professor.objects.annotate(avg_rating=Avg('ratings__rating'))

   

class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"message": "You need to log in first."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='average', permission_classes=[permissions.AllowAny])
    def average(self, request):
        professor_identifier = request.query_params.get('professor')
        module_code = request.query_params.get('module')
        if not professor_identifier or not module_code:
            return Response(
                {"error": "Professor and module query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        ratings = self.get_queryset().filter(
            professor__identifier=professor_identifier,
            module__code=module_code
        )
        avg = ratings.aggregate(average=Avg('rating'))['average']
        if avg is None:
            avg = "no ratings"
        else:
            avg = round(avg)
        return Response({"average": avg})

