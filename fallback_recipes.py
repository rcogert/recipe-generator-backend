import random

def create_fallback_recipe(ingredients, non_vegan_items, cooking_experience):
    """Create a fallback recipe when OpenAI API is unavailable"""
    
    # Parse ingredients
    ingredient_list = [ing.strip().lower() for ing in ingredients.split(',')]
    
    # Common Mediterranean ingredients
    mediterranean_bases = ['olive oil', 'garlic', 'tomatoes', 'onions', 'herbs']
    proteins = ['chickpeas', 'lentils', 'white beans', 'tofu', 'tempeh']
    vegetables = ['zucchini', 'eggplant', 'bell peppers', 'spinach', 'artichokes']
    grains = ['pasta', 'rice', 'quinoa', 'bulgur', 'couscous']
    
    # Determine what we have
    has_protein = any(p in ' '.join(ingredient_list) for p in proteins)
    has_grain = any(g in ' '.join(ingredient_list) for g in grains)
    has_tomatoes = 'tomato' in ' '.join(ingredient_list)
    has_olive_oil = 'olive oil' in ' '.join(ingredient_list)
    has_garlic = 'garlic' in ' '.join(ingredient_list)
    
    # Create substitutions for non-vegan items
    substitutions = {}
    for item in non_vegan_items:
        if 'chicken' in item.lower():
            substitutions[item] = 'chickpeas or white beans'
        elif 'cheese' in item.lower():
            substitutions[item] = 'nutritional yeast or cashew cream'
        elif 'milk' in item.lower():
            substitutions[item] = 'oat milk or almond milk'
        elif 'butter' in item.lower():
            substitutions[item] = 'olive oil or vegan butter'
        elif 'egg' in item.lower():
            substitutions[item] = 'flax egg or aquafaba'
        else:
            substitutions[item] = 'plant-based alternative'
    
    # Generate recipe based on available ingredients
    if has_tomatoes and has_garlic and has_olive_oil:
        # Mediterranean tomato-based dish
        recipe = {
            "title": "Mediterranean Tomato & Herb Pasta" if has_grain else "Mediterranean Tomato Stew",
            "difficulty": "Easy" if cooking_experience == 'new' else "Medium",
            "prep_time": "10 minutes",
            "cook_time": "20 minutes",
            "servings": "4 servings",
            "ingredients": [
                "2 tbsp olive oil",
                "3 cloves garlic, minced",
                "4 large tomatoes, diced (or 1 can crushed tomatoes)",
                "1 cup chickpeas (if available)" if not has_protein else f"Your {[p for p in proteins if p in ' '.join(ingredient_list)][0]}",
                "2 cups pasta" if has_grain else "2 cups cooked quinoa",
                "1 tsp dried oregano",
                "1 tsp dried basil",
                "Salt and pepper to taste",
                "Fresh herbs for garnish"
            ],
            "instructions": [
                "Heat olive oil in a large pan over medium heat",
                "Add minced garlic and cook for 1 minute until fragrant",
                "Add diced tomatoes and cook for 5-7 minutes",
                "Add chickpeas and herbs, simmer for 10 minutes",
                "Season with salt and pepper",
                "Serve over pasta or quinoa",
                "Garnish with fresh herbs"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": "This plant-based version is packed with fiber, antioxidants from tomatoes, and heart-healthy olive oil. The chickpeas provide complete protein while keeping it authentically Mediterranean!",
            "mediterranean_elements": "This recipe uses the classic Mediterranean flavor base of olive oil, garlic, and tomatoes - the foundation of countless traditional dishes from Greece, Italy, and Spain."
        }
    else:
        # Simple Mediterranean-style dish
        recipe = {
            "title": "Simple Mediterranean Bowl",
            "difficulty": "Easy",
            "prep_time": "15 minutes",
            "cook_time": "10 minutes",
            "servings": "2 servings",
            "ingredients": [
                "2 tbsp olive oil",
                "1 onion, diced",
                "Your available vegetables",
                "1 can chickpeas, drained",
                "1 tsp dried herbs (oregano, basil, or thyme)",
                "Salt and pepper to taste",
                "Lemon juice for serving"
            ],
            "instructions": [
                "Heat olive oil in a large pan",
                "Sauté onion until soft, about 5 minutes",
                "Add your vegetables and cook until tender",
                "Add chickpeas and herbs",
                "Cook for 5 more minutes",
                "Season with salt, pepper, and lemon juice",
                "Serve warm"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": "This flexible recipe works with whatever vegetables you have on hand! Plant-based meals like this are naturally high in fiber, vitamins, and minerals while being gentle on your wallet and the planet.",
            "mediterranean_elements": "The combination of olive oil, herbs, and fresh vegetables represents the heart of Mediterranean cooking - simple, fresh ingredients prepared with care."
        }
    
    return {
        "recipes": [recipe],
        "encouraging_message": "Great choice of ingredients! This recipe celebrates the Mediterranean tradition of creating delicious meals with simple, fresh ingredients."
    }

