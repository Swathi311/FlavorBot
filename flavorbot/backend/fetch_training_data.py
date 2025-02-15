import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Path to cached data
CACHE_FILE = "cached_recipes.json"

# Function to fetch and cache data from Firebase
def fetch_ingredients_and_recipes():
    """Fetch ingredients and recipes from Firebase in batches, only if cache is missing."""
    if os.path.exists(CACHE_FILE): 
        print("Loading cached data instead of fetching from Firebase...")
        with open(CACHE_FILE, "r") as f:
            cached_data = json.load(f)
        return set(cached_data["ingredients"]), cached_data["recipes"]

    print("Fetching data from Firebase...")
    
    # Initialize Firebase if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate("backend/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    BATCH_SIZE = 50
    ingredients = set()
    recipes = {}
    last_doc = None

    while True:
        try:
            query = db.collection("recipes").order_by("name").limit(BATCH_SIZE)
            if last_doc:
                query = query.start_after(last_doc)

            recipe_docs = query.stream()
            batch_data = list(recipe_docs)

            if not batch_data:
                break 

            for doc in batch_data:
                data = doc.to_dict()
                recipe_name = data.get("name")
                recipe_ingredients = data.get("ingredients", [])

                for ingredient in recipe_ingredients:
                    ingredient = ingredient.lower()
                    ingredients.add(ingredient)
                    recipes.setdefault(ingredient, []).append(recipe_name)

            last_doc = batch_data[-1]
            print(f"Fetched {len(batch_data)} recipes...")

        except firebase_admin.exceptions.FirebaseError as e:
            print(f"Error fetching data: {e}")
            break

    # ✅ Cache data
    with open(CACHE_FILE, "w") as f:
        json.dump({"ingredients": list(ingredients), "recipes": recipes}, f)

    print("Data fetching complete and cached.")
    return ingredients, recipes

# ✅ Load data only ONCE at module level
unique_ingredients, ingredient_to_recipes = fetch_ingredients_and_recipes()
