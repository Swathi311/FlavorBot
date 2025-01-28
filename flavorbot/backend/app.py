from flask import Flask, request, jsonify
import spacy
from flask_cors import CORS  # Import flask-cors for handling CORS
from fetch_training_data import ingredient_to_recipes

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained spaCy model
try:
    MODEL_PATH = './ner_model'  # Adjust this to your trained model's path
    nlp = spacy.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model from {MODEL_PATH}: {e}")
    nlp = None  # Set to None if the model can't be loaded

@app.route('/process', methods=['POST'])
def process_text():
    try:
        # Get the JSON payload
        data = request.get_json()
        user_input = data.get('text', '')

        if not nlp:
            return jsonify({"error": "NER model not loaded"}), 500

        # Process the text
        doc = nlp(user_input)
        entities = [{"text": ent.text.lower(), "label": ent.label_} for ent in doc.ents]

        # Fetch recipes for the detected ingredients
        detected_ingredients = [ent['text'] for ent in entities if ent['label'] == "INGREDIENT"]
        response_recipes = {}

        for ingredient in detected_ingredients:
            recipes = ingredient_to_recipes.get(ingredient, [])
            response_recipes[ingredient] = recipes

        # Response to frontend
        return jsonify({"recipes": response_recipes})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)



