from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)

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

        # Extract entities
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        print(f"Extracted entities: {entities}")

        # Return the extracted entities as the response
        return jsonify({"entities": entities})

    except Exception as e:
        # Log any errors
        print(f"Error in /process: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
