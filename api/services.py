import joblib
import os
import pandas as pd
import numpy as np
from django.conf import settings
from .models import PredictionHistory
from common.utils import get_trait_description

class PredictionService:
    def execute_model(self, model_params):
        # Path to model
        model_path = os.path.join(settings.BASE_DIR, "best_model.pkl")
        model = joblib.load(model_path)

        # Expected features from training (order matters)
        feature_columns = [
            "EXT1",
            "EXT3",
            "EXT5",
            "AGR1",
            "AGR3",
            "AGR5",
            "CSN1",
            "CSN3",
            "CSN5",
            "EST1",
            "EST3",
            "EST5",
            "OPN1",
            "OPN3",
            "OPN5",
        ]

        # Ensure correct order and fill missing
        input_vector = [model_params.get(feat, 0) for feat in feature_columns]

        # Reshape to 2D array (1 sample, n features)
        input_array = np.array(input_vector).reshape(1, -1)

        # Make prediction (returns 5 scores)
        prediction = model.predict(input_array)[0]

        # Rasgo names
        rasgo_names = ['EXT', 'AGR', 'CSN', 'EST', 'OPN']

        # Return scores clamped 1-5, scaled to 1-10
        result = {}
        for i, rasgo in enumerate(rasgo_names):
            # Clamping to 1-5 (based on training range) and scaling to 1-10
            valor_clamp = float(np.clip(prediction[i], 1.0, 5.0))
            result[rasgo] = round(valor_clamp * 2, 2)

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
