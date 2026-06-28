import os
import requests
import numpy as np
from django.conf import settings
from .models import PredictionHistory
from common.utils import get_trait_description

class PredictionService:
    def execute_model(self, model_params):
        # Call external model service prediction endpoint
        url = settings.MODEL_SERVICE_URL
        url = url.rstrip("/") + "/predict/"

        response = requests.post(url, json=model_params)
        print(f"Model service response: {response.status_code}, {response.text}")
        response.raise_for_status()

        prediction = response.json()

        # Rasgo names
        rasgo_names = ['EXT', 'AGR', 'CSN', 'EST', 'OPN']

        # Return scores clamped 1-10
        result = {}
        for rasgo in rasgo_names:
            score = prediction.get(rasgo, 0.0)
            # Clamping to 1-10
            result[rasgo] = round(float(np.clip(score, 1.0, 10.0)), 2)

        return result

    def get_prediction(self, user, model_params):
        # 1. execute_model()
        trait_scores_raw = self.execute_model(model_params)

        # 2. Construct structured scores and find intensity
        trait_data = {}
        trait_levels = {}
        for trait, score in trait_scores_raw.items():
            level = PredictionHistory.find_intensity(score)
            trait_data[trait] = {'score': score, 'level': level}
            trait_levels[trait] = level

        # 3. get_trait_description for all traits
        trait_descriptions = get_trait_description(trait_levels)

        # 4. create a radar chart data format obj
        graphics_data = {"labels": list(trait_scores_raw.keys()), "data": [v['score'] for v in trait_data.values()]}

        # 5. PredictionHistory.save()
        prediction_history = PredictionHistory.objects.create(
            user=user,
            answers_data=model_params,
            predicted_scores=trait_data,
            trait_descriptions=trait_descriptions,
            graphics_data=graphics_data
        )

        return prediction_history
