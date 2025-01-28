import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("backend/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

# Fetch data from the 'recipes' collection
def fetch_ingredients_and_recipes():
    ingredients = set()  # Store unique ingredients
    recipes = {}  # Map each ingredient to recipes

    # Assuming your collection is called "recipes"
    recipe_docs = db.collection("recipes").stream()
    for doc in recipe_docs:
        data = doc.to_dict()
        recipe_name = data.get("name")
        recipe_ingredients = data.get("ingredients", [])  # List of ingredients
        for ingredient in recipe_ingredients:
            ingredients.add(ingredient.lower())  # Normalize ingredient names
            recipes.setdefault(ingredient.lower(), []).append(recipe_name)

    return ingredients, recipes

# Test the function (Optional)
if __name__ == "__main__":
    unique_ingredients, ingredient_to_recipes = fetch_ingredients_and_recipes()