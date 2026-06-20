from .models import PredictionHistory, PersonalityProfile, CustomUser
from common.utils import get_trait_conclusions
import numpy as np
from django.utils import timezone

def update_personality_profile(user):
    # 1. Query user related PredictionHistory
    histories = PredictionHistory.objects.filter(user=user).order_by('created_at')
    
    # 2. If none, return
    if not histories.exists():
        return

    # 4. Do calculations
    # 5. Calculate historic fields
    latest_history = histories.latest('created_at')
    latest_test_scores = latest_history.predicted_scores
    first_history = histories.first()
    
    traits = ['EXT', 'AGR', 'CSN', 'EST', 'OPN']
    
    historical_graphics_data = {
        "line_chart": {
            "title": "Trait Evolution Timeline",
            "x_axis_labels": [h.created_at.strftime("%b %Y") for h in histories],
            "datasets": []
        },
        "comparison_radar_chart": {
            "title": "Baseline Shift (First vs. Latest)",
            "labels": traits,
            "datasets": [
                {
                    "label": "Initial Baseline",
                    "data": [first_history.predicted_scores.get(trait, {}).get('score', 0) for trait in traits]
                },
                {
                    "label": "Current Status",
                    "data": [latest_history.predicted_scores.get(trait, {}).get('score', 0) for trait in traits]
                }
            ]
        }
    }
    
    # Building datasets for line_chart
    for trait in traits:
        data = [h.predicted_scores.get(trait, {}).get('score', 0) for h in histories]
        historical_graphics_data["line_chart"]["datasets"].append({
            "label": trait,
            "data": data
        })

    # 6. Calculate mathematical fields
    total_tests_taken = histories.count()
    
    # Simple dominant trait logic: sum of scores
    trait_sums = {trait: 0 for trait in traits}
    for h in histories:
        for trait, data in h.predicted_scores.items():
            trait_sums[trait] += data.get('score', 0)
    primary_dominant_trait = max(trait_sums, key=trait_sums.get)
    
    # Highest variance trait
    trait_variances = {trait: 0 for trait in traits}
    for trait in traits:
        scores = [h.predicted_scores.get(trait, {}).get('score', 0) for h in histories]
        trait_variances[trait] = np.var(scores)
    highest_variance_trait = max(trait_variances, key=trait_variances.get)
    
    # 7. Static data fields
    trait_levels = {trait: latest_history.predicted_scores.get(trait, {}).get('level', 'medium') for trait in traits}
    conclusions = get_trait_conclusions(trait_levels)
    
    # Mapping to requested fields
    mapping = {
        'OPN': 'openness_conclusions',
        'CSN': 'conscientiousness_conclusions',
        'EXT': 'extraversion_conclusions',
        'AGR': 'agreeableness_conclusions',
        'EST': 'neuroticism_conclusions'
    }
    
    conclusion_data = {}
    for trait, field in mapping.items():
        data = conclusions.get(trait, {"conclusion": "", "level": ""})
        conclusion_data[field] = {
            "overall_percentage": str(latest_history.predicted_scores.get(trait, {}).get('score', 0) / 10),
            "level": data["level"],
            "conclusion": data["conclusion"]
        }

    # 8. AI fields (Generic)
    ai_summary = "Estás progresando mucho en la comprensión de tus rasgos de personalidad."
    ai_trends_analysis = "Tus tendencias parecen muy alentadoras; continúa monitoreando tu crecimiento personal."
    ai_recommendation = "Sigue adelante, tu dedicación al autoconocimiento es inspiradora."
    
    # 9. Query user related PersonalityProfile
    profile, created = PersonalityProfile.objects.get_or_create(user=user, defaults={
        'first_test_date': first_history.created_at,
        'first_test_scores': first_history.predicted_scores,
        'total_tests_taken': total_tests_taken,
        'primary_dominant_trait': primary_dominant_trait,
        'highest_variance_trait': highest_variance_trait,
        'ai_summary': ai_summary,
        'ai_trends_analysis': ai_trends_analysis,
        'ai_recommendation': ai_recommendation,
        'latest_test_scores': latest_test_scores,
        'historical_graphics_data': historical_graphics_data,
        **conclusion_data
    })
    
    if not created:
        profile.total_tests_taken = total_tests_taken
        profile.primary_dominant_trait = primary_dominant_trait
        profile.highest_variance_trait = highest_variance_trait
        profile.ai_summary = ai_summary
        profile.ai_trends_analysis = ai_trends_analysis
        profile.ai_recommendation = ai_recommendation
        profile.latest_test_scores = latest_test_scores
        profile.historical_graphics_data = historical_graphics_data
        for field, data in conclusion_data.items():
            setattr(profile, field, data)
        profile.save()
