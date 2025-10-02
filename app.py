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
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        cooking_experience = data.get('cooking_experience', 'new')
        dietary_interest = data.get('dietary_interest', 'just_curious')
        ingredients = data.get('ingredients', '')
        
        if not ingredients.strip():
            return jsonify({
                'success': False,
                'error': 'Please provide some ingredients to work with!'
            }), 400
        
        # Analyze ingredients for non-vegan items
        non_vegan_items = detect_non_vegan_ingredients(ingredients)
        
        # Generate prompt
        prompt = create_recipe_prompt(cooking_experience, dietary_interest, ingredients, non_vegan_items)
        
        # Call OpenAI API or use fallback
        try:
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            response_content = response.choices[0].message.content.strip()
            
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            recipe_data = json.loads(response_content)
        except:
            recipe_data = create_fallback_recipe(ingredients, non_vegan_items, cooking_experience)
        
        return jsonify({
            'success': True,
            'recipes': recipe_data['recipes'],
            'encouraging_message': recipe_data.get('encouraging_message', ''),
            'substitutions_made': len(non_vegan_items) > 0,
            'non_vegan_items_detected': non_vegan_items
        })
        
    except Exception as e:
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
        
        # AWeber Integration
        try:
            name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            
            aweber_data = {
                'listname': 'awlist6861386',
                'redirect': 'https://www.aweber.com/thankyou-coi.htm?m=text',
                'meta_required': 'name,email',
                'meta_tooltip': '',
                'meta_split_id': '',
                'unit': '919276201',
                'name': name,
                'email': email,
                'submit': 'Submit'
            }
            
            aweber_response = requests.post(
                'https://www.aweber.com/scripts/addlead.pl',
                data=aweber_data,
                timeout=10
             )
            
        except Exception as aweber_error:
            print(f"AWeber integration error: {aweber_error}")
        
        return jsonify({
            'success': True,
            'message': 'Great! Your recipe has been saved. Check your email shortly!'
        })
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sorry, something went wrong. Please try again.'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
