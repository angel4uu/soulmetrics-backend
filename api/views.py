from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, PredictionInputSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .services import PredictionService
from .models import PredictionHistory, PersonalityProfile
from common.utils import get_test_questions
from .tasks import update_personality_profile
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class QuestionsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        questions = get_test_questions()
        return Response(questions, status=status.HTTP_200_OK)

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
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data, status=status.HTTP_200_OK)

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

class PersonalityProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # 0. TODO: Exec update_personality_profile
        # TODO: Implement async execution (Celery)
        update_personality_profile(request.user)

        # 1. Query user related PersonalityProfile
        try:
            profile = PersonalityProfile.objects.get(user=request.user)

            # 3. If yes continue
            # 4. Return has_personality_profile True and PersonalityProfile in expected json structure

            days_active = (timezone.now() - profile.first_test_date).days

            return Response({
                "id": profile.id,
                "user_id": profile.user_id,
                "has_personality_profile": True,
                "last_updated": profile.updated_at,
                "report_metadata": {
                    "total_tests_taken": profile.total_tests_taken,
                    "first_test_date": profile.first_test_date,
                    "days_active": days_active,
                    "primary_dominant_trait": profile.primary_dominant_trait,
                    "highest_variance_trait": profile.highest_variance_trait
                },
                "ai_conclusions": {
                    "summary": profile.ai_summary,
                    "trends_analysis": profile.ai_trends_analysis,
                    "recommendation": profile.ai_recommendation
                },
                "traits_conclusions":{
                    "Openness": profile.openness_conclusions,
                    "Conscientiousness": profile.conscientiousness_conclusions,
                    "Extraversion": profile.extraversion_conclusions,
                    "Agreeableness": profile.agreeableness_conclusions,
                    "Neuroticism": profile.neuroticism_conclusions
                },
                "historical_baselines": {
                    "first_test_scores": profile.first_test_scores,
                    "latest_test_scores": profile.latest_test_scores
                },
                "graphics_data": profile.historical_graphics_data
            }, status=status.HTTP_200_OK)

        except PersonalityProfile.DoesNotExist:
            # 2. if none, return has_personality_profile False and variable with all rest empty fields
            return Response({
                "has_personality_profile": False,
                "report_metadata": {},
                "ai_conclusions": {},
                "traits_conclusions": {},
                "historical_baselines": {},
                "graphics_data": {}
            }, status=status.HTTP_200_OK)


class PersonalityProfileExportView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        try:
            profile = PersonalityProfile.objects.get(user=request.user)

        except PersonalityProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        # ---- PDF RESPONSE ----
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="personality_report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()

        content = []

        # TITLE
        content.append(Paragraph("Personality Report", styles["Title"]))
        content.append(Spacer(1, 12))

        # SUMMARY
        content.append(Paragraph("Summary", styles["Heading2"]))
        content.append(Paragraph(profile.ai_summary or "No summary available", styles["BodyText"]))
        content.append(Spacer(1, 12))

        # TRAITS
        content.append(Paragraph("Traits Analysis", styles["Heading2"]))

        traits = {
            "Openness": profile.openness_conclusions,
            "Conscientiousness": profile.conscientiousness_conclusions,
            "Extraversion": profile.extraversion_conclusions,
            "Agreeableness": profile.agreeableness_conclusions,
            "Neuroticism": profile.neuroticism_conclusions,
        }

        for key, value in traits.items():
            content.append(Paragraph(f"{key}", styles["Heading3"]))
            content.append(Paragraph(str(value), styles["BodyText"]))
            content.append(Spacer(1, 8))

        # METADATA
        content.append(Paragraph("Metadata", styles["Heading2"]))

        days_active = (timezone.now() - profile.first_test_date).days

        meta = f"""
        Total tests: {profile.total_tests_taken}<br/>
        Days active: {days_active}<br/>
        Primary trait: {profile.primary_dominant_trait}<br/>
        Highest variance: {profile.highest_variance_trait}
        """

        content.append(Paragraph(meta, styles["BodyText"]))

        doc.build(content)

        return response