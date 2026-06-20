from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)

class PredictionHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answers_data = models.JSONField(default=dict)
    predicted_scores = models.JSONField(default=dict)
    trait_descriptions = models.JSONField(default=dict)
    graphics_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def find_intensity(prediction_score):
        # Assuming score is 1-10
        if prediction_score >= 8.5:
            return "excellent"
        elif prediction_score >= 6:
            return "high"
        elif prediction_score >= 3.5:
            return "medium"
        else:
            return "low"

class PersonalityProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    # historical fields
    first_test_date = models.DateTimeField()
    first_test_scores = models.JSONField()
    # updated per prediction fields
    total_tests_taken = models.IntegerField()
    primary_dominant_trait = models.CharField(max_length=3)
    highest_variance_trait = models.CharField(max_length=3)
    ai_summary = models.TextField()
    ai_trends_analysis = models.TextField()
    ai_recommendation = models.TextField()
    openness_conclusions = models.JSONField()
    conscientiousness_conclusions = models.JSONField()
    extraversion_conclusions = models.JSONField()
    agreeableness_conclusions = models.JSONField()
    neuroticism_conclusions = models.JSONField()
    latest_test_scores = models.JSONField()
    historical_graphics_data = models.JSONField()
