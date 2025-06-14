import os
import base64
import json
import requests
from io import BytesIO
from PIL import Image
from flask import current_app

class OpenRouterAI:
    # Class variable to store analysis results
    _analysis_cache = {}
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
        self.model = 'google/gemini-2.5-flash-preview-05-20'  # Using Gemini model as specified in memory
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set it in the .env file or pass it to the constructor.")
    
    def _encode_image(self, image_file):
        """Encode image to base64 for API request"""
        try:
            # If image_file is a file path
            if isinstance(image_file, str):
                with open(image_file, 'rb') as img_file:
                    img = Image.open(BytesIO(img_file.read()))
                    # Convert to RGB if needed (e.g., for PNG with transparency)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
            # If image_file is already a file object
            else:
                img = Image.open(image_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error encoding image: {str(e)}")
    
    def get_cached_analysis(self, analysis_id):
        """Retrieve a cached analysis result by ID"""
        return self._analysis_cache.get(analysis_id)
    
    def analyze_food_image(self, image_file):
        """Analyze food image and return nutrition data"""
        try:
            base64_image = self._encode_image(image_file)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a nutrition analysis AI specializing in food identification and nutritional analysis. Your primary task is to accurately identify the specific food items in images and provide detailed nutritional information. Always provide a specific, descriptive food name rather than generic terms like "Unknown Food". If you see multiple food items, identify the main dish or list the primary components.'
                    },
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'Analyze this food image and provide: 1) A SPECIFIC and DESCRIPTIVE food name (never use "Unknown Food"), 2) Accurate nutritional content with EXACT NUMERIC VALUES (not ranges) for calories, protein, carbs, and fat. Return your analysis in JSON format with the following fields: food_description (be specific and descriptive), calories (as a single integer), protein (as a single decimal number in grams), carbs (as a single decimal number in grams), fat (as a single decimal number in grams). If you are uncertain about exact values, provide your best estimate as a single number, not a range.'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{base64_image}'
                                }
                            }
                        ]
                    }
                ],
                'response_format': {'type': 'json_object'}
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the JSON content from the response
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            # Parse the JSON content
            try:
                nutrition_data = json.loads(content)
                # Ensure we have the required fields
                required_fields = ['food_description', 'calories', 'protein', 'carbs', 'fat']
                for field in required_fields:
                    if field not in nutrition_data:
                        if field == 'food_description':
                            # Try to infer a food name from other fields or use a better default
                            if 'food_category' in nutrition_data and nutrition_data['food_category'] != 'other':
                                nutrition_data[field] = f"{nutrition_data['food_category'].capitalize()} dish"
                            else:
                                nutrition_data[field] = 'Nutritional food item'
                        else:
                            nutrition_data[field] = 0
                
                # Add default values for optional fields if not present
                nutrition_data.setdefault('fiber', 0)
                nutrition_data.setdefault('sugar', 0)
                nutrition_data.setdefault('sodium', 0)
                nutrition_data.setdefault('quantity', 1)
                nutrition_data.setdefault('unit', 'serving')
                nutrition_data.setdefault('food_category', 'other')
                
                # Generate a unique analysis ID and cache the result
                import uuid
                analysis_id = str(uuid.uuid4())
                nutrition_data['analysis_id'] = analysis_id
                
                # Add image URL if provided
                if isinstance(image_file, str) and os.path.exists(image_file):
                    # Extract the filename from the path
                    filename = os.path.basename(image_file)
                    # Construct the URL to the uploaded image
                    nutrition_data['image_url'] = f"/static/uploads/{filename}"
                
                # Cache the result
                self._analysis_cache[analysis_id] = nutrition_data
                
                return nutrition_data
            except json.JSONDecodeError as json_e:
                current_app.logger.error(f"Failed to parse JSON response from AI: {content}. Error: {json_e}")
                # Return an error so the frontend knows something went wrong
                return {'error': 'AI response format error. Could not parse nutrition data.'}
        
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API request error: {str(e)}")
            error_detail = f"API request failed: {str(e)}"
            if e.response is not None:
                error_detail = f"API request failed with status {e.response.status_code}. Response: {e.response.text[:200]}..."
            return {'error': error_detail}
        except Exception as e:
            current_app.logger.error(f"Error analyzing food image: {str(e)}")
            return {'error': f"Error analyzing food image: {str(e)}"}
    
    def _extract_nutrition_from_text(self, text):
        """Fallback method to extract nutrition data from text response"""
        # Default values
        nutrition_data = {
            'food_description': 'Food item',  # Generic but not 'Unknown food'
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0,
            'quantity': 1,
            'unit': 'serving',
            'food_category': 'other'
        }
        
        # Try to find common nutrition keywords in the text
        if 'calories' in text.lower():
            # Simple regex or string parsing could be implemented here
            # For now, we'll return default values
            pass
        
        return nutrition_data
    
    def generate_personalized_tip(self, user_data, goals):
        """Generate a personalized nutrition tip based on user data and goals"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare user data for the prompt
            user_info = f"User's daily goals: {goals['calories']} calories, {goals['protein']}g protein, "
            user_info += f"{goals['carbs']}g carbs, {goals['fat']}g fat."
            
            if 'recent_entries' in user_data and user_data['recent_entries']:
                user_info += " Recent food entries: "
                for entry in user_data['recent_entries'][:3]:  # Include up to 3 recent entries
                    user_info += f"{entry['food_description']} ({entry['calories']} cal), "
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a nutrition coach providing personalized tips. Keep tips concise, actionable, and evidence-based.'
                    },
                    {
                        'role': 'user',
                        'content': f"Generate a short, personalized nutrition tip for a user with the following data: {user_info}"
                    }
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            tip_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            return {
                'tip_text': tip_text.strip(),
                'category': 'personalized'
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating tip: {str(e)}")
            return {
                'tip_text': "Try to include a variety of colorful fruits and vegetables in your diet. Each color provides different phytonutrients and antioxidants that support your immune system and overall health.",
                'category': 'general'  # Fallback to general tip
            }
