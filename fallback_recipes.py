import random

def create_fallback_recipe(ingredients, non_vegan_items, cooking_experience):
    """Create a fallback recipe when OpenAI API is unavailable"""
    
    # Parse ingredients
    ingredient_list = [ing.strip().lower() for ing in ingredients.split(',')]
    ingredients_text = ' '.join(ingredient_list)
    
    # Common Mediterranean ingredients
    proteins = ['chickpeas', 'lentils', 'white beans', 'black beans', 'tofu', 'tempeh']
    vegetables = ['zucchini', 'eggplant', 'bell peppers', 'spinach', 'artichokes', 'mushrooms', 'onions', 'carrots']
    grains = ['pasta', 'rice', 'quinoa', 'bulgur', 'couscous', 'orzo']
    herbs = ['basil', 'oregano', 'thyme', 'rosemary', 'parsley']
    
    # Determine what we have
    has_tomatoes = any(word in ingredients_text for word in ['tomato', 'tomatoes'])
    has_olive_oil = 'olive oil' in ingredients_text
    has_garlic = 'garlic' in ingredients_text
    has_onion = any(word in ingredients_text for word in ['onion', 'onions'])
    has_pasta = any(word in ingredients_text for word in grains)
    has_protein = any(word in ingredients_text for word in proteins)
    has_vegetables = any(word in ingredients_text for word in vegetables)
    has_herbs = any(word in ingredients_text for word in herbs)
    
    # Find specific ingredients mentioned
    found_proteins = [p for p in proteins if p in ingredients_text]
    found_vegetables = [v for v in vegetables if v in ingredients_text]
    found_grains = [g for g in grains if g in ingredients_text]
    found_herbs = [h for h in herbs if h in ingredients_text]
    
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
    if has_tomatoes and has_garlic:
        # Mediterranean tomato-based dish
        main_protein = found_proteins[0] if found_proteins else 'chickpeas'
        main_grain = found_grains[0] if found_grains else 'pasta'
        
        recipe = {
            "title": f"Mediterranean {main_protein.title()} with {main_grain.title()}",
            "difficulty": "Easy" if cooking_experience == 'new' else "Medium",
            "prep_time": "10 minutes",
            "cook_time": "20 minutes",
            "total_time": "30 minutes",
            "servings": "4 servings",
            "ingredients": [
                "2 tbsp olive oil",
                "3 cloves garlic, minced",
                "4 large tomatoes, diced (or 1 can crushed tomatoes)",
                f"1 cup {main_protein}",
                f"2 cups {main_grain}",
                "1 tsp dried oregano",
                "1 tsp dried basil",
                "Salt and pepper to taste",
                "Fresh herbs for garnish"
            ],
            "instructions": [
                "Heat olive oil in a large pan over medium heat",
                "Add minced garlic and cook for 1 minute until fragrant",
                "Add diced tomatoes and cook for 5-7 minutes until softened",
                f"Add {main_protein} and herbs, simmer for 10 minutes",
                "Season with salt and pepper to taste",
                f"Serve over cooked {main_grain}",
                "Garnish with fresh herbs and a drizzle of olive oil"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": f"This plant-based version features {main_protein} which provides excellent protein and fiber, while the tomatoes add lycopene and the olive oil provides heart-healthy fats!",
            "mediterranean_elements": "This recipe uses the classic Mediterranean flavor base of olive oil, garlic, and tomatoes - the foundation of countless traditional dishes from Greece, Italy, and Spain."
        }
        
    elif has_vegetables and has_olive_oil:
        # Mediterranean vegetable dish
        main_vegetables = found_vegetables[:2] if len(found_vegetables) >= 2 else found_vegetables + ['bell peppers']
        main_protein = found_proteins[0] if found_proteins else 'white beans'
        
        recipe = {
            "title": f"Mediterranean {' & '.join([v.title() for v in main_vegetables])} Bowl",
            "difficulty": "Easy",
            "prep_time": "15 minutes",
            "cook_time": "15 minutes",
            "total_time": "30 minutes",
            "servings": "3 servings",
            "ingredients": [
                "3 tbsp olive oil",
                "1 onion, diced",
                f"2 cups {main_vegetables[0]}, chopped",
                f"1 cup {main_vegetables[1] if len(main_vegetables) > 1 else 'zucchini'}, diced",
                f"1 can {main_protein}, drained and rinsed",
                "2 tsp dried Mediterranean herbs",
                "Salt and pepper to taste",
                "Lemon juice for serving",
                "Fresh parsley for garnish"
            ],
            "instructions": [
                "Heat olive oil in a large skillet over medium heat",
                "Add onion and cook until softened, about 5 minutes",
                f"Add {main_vegetables[0]} and cook for 5 minutes",
                f"Add {main_vegetables[1] if len(main_vegetables) > 1 else 'zucchini'} and cook for 3 minutes",
                f"Stir in {main_protein} and herbs",
                "Cook for 5 more minutes until heated through",
                "Season with salt, pepper, and fresh lemon juice",
                "Garnish with fresh parsley and serve"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": f"This colorful dish is packed with vitamins from the {' and '.join(main_vegetables)}, plus plant protein from {main_protein}. It's naturally anti-inflammatory and heart-healthy!",
            "mediterranean_elements": "The generous use of olive oil, fresh vegetables, and herbs reflects the Mediterranean emphasis on simple, high-quality ingredients that let natural flavors shine."
        }
        
    elif has_pasta or found_grains:
        # Mediterranean grain/pasta dish
        main_grain = found_grains[0] if found_grains else 'pasta'
        main_protein = found_proteins[0] if found_proteins else 'chickpeas'
        
        recipe = {
            "title": f"Mediterranean {main_grain.title()} Primavera",
            "difficulty": "Easy",
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "total_time": "25 minutes",
            "servings": "4 servings",
            "ingredients": [
                f"2 cups {main_grain}",
                "3 tbsp olive oil",
                "2 cloves garlic, minced",
                "Your available vegetables, chopped",
                f"1 cup {main_protein}",
                "1 tsp Italian seasoning",
                "Salt and pepper to taste",
                "Nutritional yeast for serving (optional)"
            ],
            "instructions": [
                f"Cook {main_grain} according to package directions",
                "Heat olive oil in a large pan",
                "Add garlic and cook for 30 seconds",
                "Add your vegetables and cook until tender-crisp",
                f"Add {main_protein} and Italian seasoning",
                "Toss with cooked pasta and season to taste",
                "Serve with nutritional yeast if desired"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": f"This satisfying dish combines complex carbs from {main_grain} with plant protein from {main_protein}, creating a complete and nourishing meal!",
            "mediterranean_elements": "This style of pasta with olive oil, garlic, and fresh ingredients is a staple throughout the Mediterranean, especially in Italy and Greece."
        }
        
    else:
        # Simple Mediterranean-style dish with whatever they have
        recipe = {
            "title": "Mediterranean Herb & Olive Oil Bowl",
            "difficulty": "Easy",
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "total_time": "25 minutes",
            "servings": "2 servings",
            "ingredients": [
                "3 tbsp extra virgin olive oil",
                "Your available ingredients, prepared as needed",
                "1 tsp dried Mediterranean herbs (oregano, basil, thyme)",
                "2 cloves garlic, minced (if available)",
                "Salt and pepper to taste",
                "Fresh lemon juice",
                "Optional: chickpeas or white beans for protein"
            ],
            "instructions": [
                "Heat olive oil in a large pan over medium heat",
                "Add garlic (if using) and cook for 30 seconds",
                "Add your heartier ingredients first (root vegetables, grains)",
                "Add quicker-cooking ingredients (leafy greens, herbs)",
                "Season with Mediterranean herbs, salt, and pepper",
                "Finish with fresh lemon juice",
                "Serve warm, drizzled with extra olive oil"
            ],
            "substitutions_made": substitutions,
            "why_plant_based_rocks": "This flexible approach lets you create a nutritious meal with whatever you have on hand! The olive oil provides healthy fats while herbs add antioxidants and amazing flavor.",
            "mediterranean_elements": "The combination of quality olive oil, fresh herbs, and simple preparation is the essence of Mediterranean cooking - letting each ingredient's natural flavor shine."
        }
    
    return {
        "recipes": [recipe],
        "encouraging_message": f"Wonderful ingredient choices! You're creating an authentic Mediterranean-style dish that celebrates the region's tradition of simple, flavorful cooking with {', '.join(ingredient_list[:3])}{'...' if len(ingredient_list) > 3 else ''}."
    }
