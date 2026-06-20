from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import joblib
from rest_framework.views import APIView
import os
import pandas as pd
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
        try:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'best_model.pkl')
            model = joblib.load(model_path)
            
            # Extract data from request
            data = request.data
            
            # Define the expected feature columns in the correct order
            feature_columns = ['EST1', 'EST2', 'EST3', 'EST4','EST5','EST6', 'EST7', 'EST8', 'EST9', 'EST10', 
                               'AGR1', 'AGR2', 'AGR3', 'AGR4', 'AGR5','AGR6', 'AGR7', 'AGR8', 'AGR9', 'AGR10', 
                               'CSN1', 'CSN2','CSN3', 'CSN4', 'CSN5','CSN6', 'CSN7', 'CSN8', 'CSN9', 'CSN10', 
                               'OPN1', 'OPN2', 'OPN3', 'OPN4', 'OPN5','OPN6', 'OPN7', 'OPN8', 'OPN9', 'OPN10', 
                               'EST1_E','EST2_E', 'EST3_E', 'EST4_E','EST5_E','EST6_E', 'EST7_E', 'EST8_E', 'EST9_E', 'EST10_E', 
                               'AGR1_E','AGR2_E', 'AGR3_E', 'AGR4_E', 'AGR5_E','AGR6_E', 'AGR7_E', 'AGR8_E','AGR9_E', 'AGR10_E', 
                               'CSN1_E', 'CSN2_E', 'CSN3_E', 'CSN4_E', 'CSN5_E','CSN6_E', 'CSN7_E', 'CSN8_E', 'CSN9_E', 'CSN10_E', 
                               'OPN1_E', 'OPN2_E','OPN3_E', 'OPN4_E', 'OPN5_E', 'OPN6_E', 'OPN7_E', 'OPN8_E', 'OPN9_E', 'OPN10_E']            
            # Create a pandas DataFrame from the input data
            input_df = pd.DataFrame([data], columns=feature_columns)
            
            # Ensure all columns are present, fill missing with 0
            for col in feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            # Ensure the order of columns matches the training data
            input_df = input_df[feature_columns]

            # Make prediction
            prediction = model.predict(input_df)

            result = prediction.tolist()[0]

            if result >= 4:
                nivel = "Muy extrovertido"
            elif result >= 3:
                nivel = "Extrovertido"
            elif result >= 2:
                nivel = "Neutral"
            else:
                nivel = "Introvertido"

            PredictionHistory.objects.create(
                user=request.user,
                predicted_scores={"score": float(result)},
                trait_descriptions={"level": nivel},
                answers_data=dict(data),
                graphics_data={},
                
            )

            return Response({
                "status": "success",
                "personality_prediction": result,
                "personality_type": nivel,
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