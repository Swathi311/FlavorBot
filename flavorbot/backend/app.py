from flask import Flask, request, jsonify
import spacy
from flask_cors import CORS  
from fetch_training_data import ingredient_to_recipes
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Initialize Firestore (Avoid multiple initializations)
if not firebase_admin._apps:
    cred = credentials.Certificate("backend/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Load the trained spaCy model
try:
    MODEL_PATH = './ner_model'
    nlp = spacy.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    nlp = None  

@app.route('/process', methods=['POST'])
def process_text():
    try:
        data = request.get_json()
        user_input = data.get('text', '')

        if not nlp:
            return jsonify({"error": "NER model not loaded"}), 500

        doc = nlp(user_input)
        entities = [{"text": ent.text.lower(), "label": ent.label_} for ent in doc.ents]

        detected_ingredients = [ent['text'] for ent in entities if ent['label'] == "INGREDIENT"]
        response_recipes = {}

        for ingredient in detected_ingredients:
            recipe_names = ingredient_to_recipes.get(ingredient, [])

            if recipe_names:
                full_recipes = []
                for recipe_name in recipe_names:
                    query = db.collection("recipes").where("name", "==", recipe_name).limit(1).stream()
                    for doc in query:
                        recipe_data = doc.to_dict()
                        full_recipes.append({
                            "name": recipe_data.get("name"),
                            "description": recipe_data.get("description", "No description available."),
                            "ingredients": recipe_data.get("ingredients", []),
                            "instructions": recipe_data.get("instructions", []),
                            "prep_time": recipe_data.get("prep_time", "Unknown"),
                            "cook_time": recipe_data.get("cook_time", "Unknown"),
                            "image_url": recipe_data.get("image_url", "")
                        })
                
                response_recipes[ingredient] = full_recipes

        return jsonify({
    "recipes": {
        ingredient: [recipe for recipe in full_recipes]
        for ingredient, full_recipes in response_recipes.items()
    }
})


    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
