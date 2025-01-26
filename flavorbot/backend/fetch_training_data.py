import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("backend/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

# Fetch data from the 'recipes' collection
def fetch_recipes():
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()
    
    training_data = []
    
    for doc in docs:
        recipe = doc.to_dict()
        ingredients = recipe.get("ingredients", [])
        
        # Format the training data
        for ingredient in ingredients:
            start_index = recipe['description'].lower().find(ingredient.lower())
            if start_index != -1:
                end_index = start_index + len(ingredient)
                training_data.append((
                    recipe['description'], 
                    {"entities": [(start_index, end_index, "INGREDIENT")]}
                ))
    
    return training_data

# Test the function (Optional)
if __name__ == "__main__":
    training_data = fetch_recipes()
    print(training_data)
