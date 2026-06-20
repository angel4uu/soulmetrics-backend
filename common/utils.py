import json
import random
import os
from django.conf import settings

def get_test_questions():
    file_path = os.path.join(settings.BASE_DIR, 'static', 'test_questions.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def get_trait_description(trait_levels):
    """
    Look up description for each trait, aggregate into a single paragraph.
    trait_levels: dict mapping trait name (EXT, AGR, CSN, EST, OPN) to level (low, medium, high)
    """
    
    descriptions = []
    
    # Mapping for file names
    file_map = {
        'EXT': 'extraversion_descriptions.json',
        'AGR': 'agreeableness_descriptions.json',
        'CSN': 'conscientiousness_descriptions.json',
        'EST': 'neuroticism_descriptions.json', # Note: mapping EST to neuroticism based on typical usage
        'OPN': 'openness_descriptions.json'
    }
    
    for trait, level in trait_levels.items():
        file_name = file_map.get(trait)
        if not file_name:
            continue
            
        file_path = os.path.join(settings.BASE_DIR, 'static', file_name)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                trait_descs = data.get(level, [])
                if trait_descs:
                    descriptions.append(random.choice(trait_descs))
        except Exception:
            continue
            
    # Aggregate descriptions
    aggregated_description = " ".join(descriptions) if descriptions else "No hay descripciones disponibles."
    
    return {
        "title": "Descripcion de personalidad",
        "description": aggregated_description
    }

def get_trait_conclusions(trait_levels):
    """
    Look up conclusion for each trait.
    trait_levels: dict mapping trait name (EXT, AGR, CSN, EST, OPN) to level (low, medium, high, excellent)
    """
    conclusions = {}
    
    # Mapping for file names
    file_map = {
        'EXT': 'extraversion_conclusions.json',
        'AGR': 'agreeableness_conclusions.json',
        'CSN': 'conscientiousness_conclusions.json',
        'EST': 'neuroticism_conclusions.json',
        'OPN': 'openness_conclusions.json'
    }
    
    for trait, level in trait_levels.items():
        file_name = file_map.get(trait)
        if not file_name:
            continue
            
        file_path = os.path.join(settings.BASE_DIR, 'static', file_name)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                trait_concs = data.get(level, [])
                if trait_concs:
                    conclusions[trait] = {
                        "conclusion": random.choice(trait_concs),
                        "level": level
                    }
        except Exception:
            continue
            
    return conclusions
