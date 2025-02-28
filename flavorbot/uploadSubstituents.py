import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialize Firebase Admin SDK
cred = credentials.Certificate("backend/serviceAccountKey.json")  # Update with your file path
firebase_admin.initialize_app(cred)

# Firestore Database Reference
db = firestore.client()

# Load JSON File
with open("substituents.json", "r") as file:
    try:
        substituents = json.load(file)  # Load JSON as a dictionary
        if not isinstance(substituents, dict):  
            raise ValueError("JSON file must contain a dictionary.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Please check your file.")
        exit()

# Upload Data to Firestore
def upload_substituents():
    collection_ref = db.collection("substituents")  # Firestore collection name

    for ingredient, substitutes in substituents.items():
        doc_ref = collection_ref.document(ingredient)  # Use ingredient as document ID
        doc_ref.set({"substitutes": substitutes})  # Store substitutes as a list field
        print(f"Uploaded {ingredient} with substitutes: {substitutes}")

upload_substituents()
print("Data successfully uploaded to Firestore.")
