from flask import Flask, request, jsonify
import openai
import os
import json
import re
import requests
from datetime import datetime
from fallback_recipes import create_fallback_recipe

app = Flask(__name__)

# Manual CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configure OpenAI (using environment variable that's already set)
openai.api_key = os.getenv('OPENAI_API_KEY')

def detect_non_vegan_ingredients(ingredients_string):
    """
    Detect non-vegan ingredients in the input string
    """
    non_vegan_keywords = [
        'chicken', 'beef', 'pork', 'turkey', 'fish', 'salmon', 'tuna', 'shrimp',
        'cheese', 'milk', 'butter', 'cream', 'yogurt', 'eggs', 'egg',
        'bacon', 'ham', 'sausage', 'ground beef', 'ground turkey', 'meat',
        'dairy', 'mozzarella', 'parmesan', 'feta', 'goat cheese', 'ricotta'
    ]
    
    ingredients_lower = ingredients_string.lower()
    found_items = []
    
    for keyword in non_vegan_keywords:
        if keyword in ingredients_lower:
            found_items.append(keyword)
    
    return found_items

def create_recipe_prompt(cooking_experience, dietary_interest, ingredients, non_vegan_items):
    """
    Create the OpenAI prompt for recipe generation
    """
    prompt = f"""You are a Mediterranean culinary expert who specializes in creating delicious vegan versions of traditional recipes. You help people discover how amazing plant-based Mediterranean food can be, regardless of their current dietary preferences.

User Profile:
- Cooking Experience: {cooking_experience}
- Dietary Interest: {dietary_interest}

Available Ingredients: {ingredients}

Instructions:
1. Create 1-2 delicious Mediterranean vegan recipes using the available plant ingredients
2. For any non-vegan ingredients mentioned ({', '.join(non_vegan_items) if non_vegan_items else 'none detected'}), suggest tasty plant-based alternatives and explain why they work well
3. Make the recipes sound exciting and delicious, not like a compromise
4. Adjust complexity based on cooking experience: {"simple techniques and detailed instructions" if cooking_experience == "new" else "can include more advanced techniques"}
5. Include brief educational notes about why the plant-based version is great (health, flavor, cost, etc.)
6. Focus on authentic Mediterranean flavors and ingredients

Response Format (JSON only, no other text):
{{
  "recipes": [
    {{
      "title": "Recipe Name",
      "difficulty": "Easy" or "Intermediate",
      "prep_time": "X minutes",
      "cook_time": "X minutes", 
      "total_time": "X minutes",
      "servings": "X servings",
      "ingredients": ["ingredient with quantities"],
      "substitutions_made": {{
        "original_ingredient": "plant_alternative",
        "why_it_works": "explanation"
      }},
      "instructions": ["detailed step-by-step instructions"],
      "why_plant_based_rocks": "Brief note about benefits of this plant-based version",
      "mediterranean_elements": "What makes this authentically Mediterranean"
    }}
  ],
  "encouraging_message": "Positive message about plant-based Mediterranean cooking"
}}"""
    
    return prompt

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/generate-recipes', methods=['POST'])
def generate_recipes():
    """Generate Mediterranean vegan recipes based on user input"""
    try:
        print("=== Starting recipe generation ===")
        
        data = request.get_json()
        print(f"Request data: {data}")
        print(f"Data type: {type(data)}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        cooking_experience = data.get('cooking_experience', 'new')
        dietary_interest = data.get('dietary_interest', 'just_curious')
        ingredients = data.get('ingredients', '')
        
        print(f"Parsed values - cooking: {cooking_experience}, dietary: {dietary_interest}, ingredients: {ingredients}")
        
        if not ingredients.strip():
            return jsonify({
                'success': False,
                'error': 'Please provide some ingredients to work with!'
            }), 400
        
        # Analyze ingredients for non-vegan items
        print("=== Analyzing ingredients ===")
        non_vegan_items = detect_non_vegan_ingredients(ingredients)
        print(f"Non-vegan items detected: {non_vegan_items}")
        
        # Generate prompt
        print("=== Creating prompt ===")
        prompt = create_recipe_prompt(cooking_experience, dietary_interest, ingredients, non_vegan_items)
        print(f"Prompt created, length: {len(prompt)}")
        
        # Call OpenAI API
        print("=== Calling OpenAI API ===")
        try:
        # Use the newer OpenAI client format
         client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
         response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )


            
            print(f"OpenAI response: {response}")
            
            # Parse response
            response_content = response.choices[0].message.content.strip()
            print(f"OpenAI response content: {response_content}")
            
            # Clean up the response to ensure it's valid JSON
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            try:
                recipe_data = json.loads(response_content)
                print(f"Parsed recipe data: {recipe_data}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response content: {response_content}")
                # Use fallback recipe
                recipe_data = create_fallback_recipe(ingredients, non_vegan_items, cooking_experience)
                
        except Exception as openai_error:
            print(f"OpenAI API error: {openai_error}")
            print("Using fallback recipe generation...")
            # Use fallback recipe when OpenAI fails
            recipe_data = create_fallback_recipe(ingredients, non_vegan_items, cooking_experience)
        
        # Track user interaction for analytics
        print("=== Tracking user interaction ===")
        track_user_interaction(cooking_experience, dietary_interest, non_vegan_items, ingredients)
        
        print("=== Returning success response ===")
        return jsonify({
            'success': True,
            'recipes': recipe_data['recipes'],
            'encouraging_message': recipe_data.get('encouraging_message', ''),
            'substitutions_made': len(non_vegan_items) > 0,
            'non_vegan_items_detected': non_vegan_items
        })
        
    except Exception as e:
        import traceback
        print(f"Full error traceback: {traceback.format_exc()}")
        print(f"Error generating recipes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sorry, something went wrong generating your recipes. Please try again.'
        }), 500

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Handle email capture and AWeber integration"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        recipes = data.get('recipes', [])
        user_profile = data.get('user_profile', {})
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid email address.'
            }), 400
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'error': 'Please provide a valid email address.'
            }), 400
        
        # TODO: Integrate with AWeber
        # For now, we'll just simulate success
        # aweber_result = send_to_aweber(email, user_profile)
        
        # TODO: Send email with recipes
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Great! Your recipes have been saved. Check your email shortly!'
        })
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sorry, something went wrong. Please try again.'
        }), 500

def track_user_interaction(cooking_exp, dietary_interest, non_vegan_items, ingredients):
    """
    Track user interactions for analytics
    """
    analytics_data = {
        'cooking_experience': cooking_exp,
        'dietary_interest': dietary_interest,
        'had_non_vegan_items': len(non_vegan_items) > 0,
        'non_vegan_count': len(non_vegan_items),
        'non_vegan_items': non_vegan_items,
        'ingredient_count': len(ingredients.split(',')),
        'timestamp': datetime.now().isoformat()
    }
    
    # For now, just print to console
    # In production, this would go to your analytics service
    print(f"User interaction: {analytics_data}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

