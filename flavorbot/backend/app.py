from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
app = Flask(__name__)
CORS(app)

# Load trained spaCy model
MODEL_PATH = "../ner_model"
if os.path.exists(MODEL_PATH):
    print("Loading trained spaCy model...")
    try:
        nlp = spacy.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading spaCy model: {e}")
        nlp = None
else:
    print("Model not found! Make sure to train it first.")
    nlp = None  # Prevents crashes if model is missing

# Load cached recipes and ingredient index
CACHE_FILE = "../cached_recipes.json"
TFIDF_CACHE_FILE = "../tfidf_data.pkl"

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            cached_data = json.load(f)
        recipes = cached_data.get("recipes", [])  # Now a list
        ingredient_index = cached_data.get("ingredient_index", {})  # Maps ingredient -> recipe IDs
        print(f"Loaded {len(recipes)} unique recipes and {len(ingredient_index)} indexed ingredients.")
    except Exception as e:
        print(f"Error loading recipe cache: {e}")
        recipes, ingredient_index = [], {}
else:
    print("Recipe cache not found! Run fetch_training_data.py first.")
    recipes, ingredient_index = [], {}

# Load TF-IDF vectors
if os.path.exists(TFIDF_CACHE_FILE):
    try:
        with open(TFIDF_CACHE_FILE, "rb") as f:
            vectorizer, recipe_vectors = pickle.load(f)
        print(f"Loaded TF-IDF vectors with shape {recipe_vectors.shape}.")
    except Exception as e:
        print(f"Error loading TF-IDF data: {e}")
        vectorizer, recipe_vectors = None, None
else:
    print("TF-IDF cache not found! Run fetch_training_data.py first.")
    vectorizer, recipe_vectors = None, None  # Prevents crashes

# Load cached substituents
SUBSTITUENTS_CACHE_FILE = "../cached_substituents.json"
with open(SUBSTITUENTS_CACHE_FILE, "r") as f:
    substituents_data = json.load(f)
# Function to extract ingredients using spaCy NER
def extract_ingredients(user_input):
    if not nlp:
        print("Warning: NLP model is missing. No ingredients will be detected.")
        return []
    doc = nlp(user_input)
    ingredients = [ent.text.lower() for ent in doc.ents if ent.label_ == "INGREDIENT"]
    return ingredients

# Function to find recipes by extracted ingredients
def find_recipes_by_ingredients(detected_ingredients):
    """Retrieve recipes based on detected ingredients using the ingredient index."""
    if not detected_ingredients:
        return []
    recipe_ids = set()  # Avoid duplicate recipes
    for ingredient in detected_ingredients:
        recipe_ids.update(ingredient_index.get(ingredient, []))  # Fetch recipe IDs
    # Convert IDs to actual recipes
    return [recipe for recipe in recipes if recipe["id"] in recipe_ids]

# Function to find best recipes using TF-IDF similarity
def find_best_recipes(user_input):
    if not vectorizer or recipe_vectors is None or recipe_vectors.shape[0] == 0:
        print("Warning: TF-IDF data is missing or empty. No recommendations will be made.")
        return []
    user_vector = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vector, recipe_vectors).flatten()
    top_indices = similarities.argsort()[-1:][::-1]  # Highest to lowest similarity
    valid_indices = [i for i in top_indices if similarities[i] > 0.1]
    if not valid_indices:
        print("No relevant recipes found.")
        return []
    return [recipes[i] for i in valid_indices if i < len(recipes)] 

def get_substitutes(ingredient):
    return substituents_data.get(ingredient.lower(), [])

@app.route("/process", methods=["POST"])
def process_query():
    try:
        data = request.json
        user_input = data.get("text", "").strip().lower()

        if "yes" in user_input:
            return jsonify({"message": "Great! Enjoy cooking your chosen recipe."})

        if "no" in user_input:
            return jsonify({"message": "Which ingredient are you missing?"})

        if "missing" in user_input:
            missing_ingredient = user_input.split("missing")[-1].strip()
            substitutes = get_substitutes(missing_ingredient)
            if substitutes:
                return jsonify({"message": f"Here are some substitutes for '{missing_ingredient}': {', '.join(substitutes)}"})
            else:
                return jsonify({"message": f"Sorry, I couldn't find substitutes for '{missing_ingredient}'."})

        detected_ingredients = extract_ingredients(user_input)
        ingredient_based_recipes = find_recipes_by_ingredients(detected_ingredients)
        best_recipes = find_best_recipes(user_input)
        all_recipes = {r["id"]: r for r in ingredient_based_recipes + best_recipes}.values()

        if not all_recipes:
            return jsonify({"recipes": {}, "message": "No matching recipes found."})

        response_recipes = {}
        for recipe in all_recipes:
            response_recipes.setdefault("General", []).append({
                "name": recipe["name"],
                "description": recipe["description"],
                "ingredients": recipe["ingredients"],
                "instructions": recipe["instructions"],
                "prep_time": recipe["prep_time"],
                "cook_time": recipe["cook_time"],
            })

        return jsonify({"recipes": response_recipes, "message": "Do you have all the ingredients?"})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": "SORRY, there was an error processing your request."}), 500
if __name__ == "__main__":
    app.run(debug=True, port=8000)
