from flask import Flask, request, jsonify
import spacy
from flask_cors import CORS  # Import flask-cors for handling CORS

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
        # Get the JSON payload from the POST request
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract the user input text
        user_input = data.get('text', '')
        print(f"User input: {user_input}")

        # Check if the model is loaded
        if not nlp:
            print("NER model not loaded")
            return jsonify({"error": "NER model not loaded"}), 500

        # Process the text using the spaCy model
        doc = nlp(user_input)
        print(f"Processed text: {doc}")

        # Extract ingredients
        ingredients = [{"text": ent.text, "label": ent.label_} for ent in doc.ents if ent.label_ == "INGREDIENT"]
        print(f"Extracted ingredients: {ingredients}")

        # Check if ingredients were found and return response
        if ingredients:
            response_text = f"Here's the recipe with the ingredients: {', '.join([ing['text'] for ing in ingredients])}"
        else:
            response_text = "Sorry, no ingredients detected in your query. Could you please specify ingredients?"

        return jsonify({"response": response_text, "entities": ingredients})

    except Exception as e:
        # Log any errors
        print(f"Error in /process: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)



