from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, PredictionInputSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .services import PredictionService
from .models import PredictionHistory

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PredictionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = PredictionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = PredictionService()
            prediction_history = service.get_prediction(request.user, serializer.validated_data)


            return Response({
                "status": "success",
                "personality_prediction": prediction_history.predicted_scores,
                "trait_descriptions": prediction_history.trait_descriptions,
                "graphics_data": prediction_history.graphics_data,
                "message": "Predicción realizada correctamente"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            

class HistoryView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = None  # no necesitas serializer aún

    def get(self, request):
        history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')

        data = []
        for h in history:
            data.append({
                "id": h.id,
                "answers_data": h.answers_data,
                "predicted_scores": h.predicted_scores,
                "trait_descriptions": h.trait_descriptions,
                "graphics_data": h.graphics_data,
                "created_at": h.created_at
            })

        page = self.paginate_queryset(data)
        return self.get_paginated_response(page)

class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "occupation": user.occupation
        })

    def put(self, request):
        user = request.user

        user.age = request.data.get("age", user.age)
        user.occupation = request.data.get("occupation", user.occupation)
        user.save()

        return Response({"message": "Profile updated"})