import spacy
from spacy.training.example import Example
import json
import os
import random

MODEL_PATH = "../ner_model"

# Load query formats from training_data.json
with open("training_data.json", "r") as f:
    QUERY_FORMATS = json.load(f)

# Load unique ingredients from cached_recipes.json
with open("../cached_recipes.json", "r") as f:
    cached_data = json.load(f)

# Extract unique ingredients from recipes
unique_ingredients = set()
for recipe in cached_data["recipes"]:
    unique_ingredients.update(recipe["ingredients"])

unique_ingredients = list(unique_ingredients)  # Convert set to list

# Dynamically generate TRAIN_DATA
TRAIN_DATA = []
for ingredient in unique_ingredients:
    for query in QUERY_FORMATS:
        text = query["text"].format(ingredient)  # Insert ingredient into query

        start = text.find(ingredient)  # Find actual position
        if start == -1:
            continue  # Skip if ingredient is not found (shouldn't happen)

        end = start + len(ingredient)
        
        TRAIN_DATA.append((text, {"entities": [(start, end, "INGREDIENT")]}))

# Print sample training data
print("Generated Training Data Sample:")
for sample in TRAIN_DATA[:5]:  
    print(sample)

if os.path.exists(MODEL_PATH):
    print(f"Loading existing model from {MODEL_PATH}")
    nlp = spacy.load(MODEL_PATH)
else:
    print("Creating a new blank model...")
    nlp = spacy.blank("en")

# Ensure NER pipeline exists
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Ensure Text Classification exists
if "textcat" not in nlp.pipe_names:
    textcat = nlp.add_pipe("textcat", last=True)
else:
    textcat = nlp.get_pipe("textcat")

textcat.add_label("FIND_RECIPE")
textcat.add_label("SUBSTITUTION")
textcat.add_label("GREETING")

# ⚠️ **IMPORTANT**: Initialize the model before training
nlp.initialize()


# Sample training data for intent classification
TEXTCAT_TRAIN_DATA = [
    ("Show me a recipe for pasta", {"cats": {"FIND_RECIPE": 1.0, "SUBSTITUTION": 0.0, "GREETING": 0.0}}),
    ("I don’t have butter, what can I use?", {"cats": {"FIND_RECIPE": 0.0, "SUBSTITUTION": 1.0, "GREETING": 0.0}}),
    ("Hey there!", {"cats": {"FIND_RECIPE": 0.0, "SUBSTITUTION": 0.0, "GREETING": 1.0}})
]

# Training iterations
n_iter = 10

for itn in range(n_iter):
    print(f"Iteration {itn + 1}/{n_iter}")
    losses = {}

    random.shuffle(TRAIN_DATA)  # Shuffle for better learning

    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        try:
            nlp.update([example], losses=losses, drop=0.3)
        except Exception as e:
            print(f"Error during NER training: {e}")
    
    for text, annotations in TEXTCAT_TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        try:
            nlp.update([example], losses=losses, drop=0.3)
        except Exception as e:
            print(f"Error during TextCat training: {e}")
    
    print(f"Iteration {itn + 1} Losses: {losses}")

# Save updated model
nlp.to_disk(MODEL_PATH)
print(f"Model updated and saved to {MODEL_PATH}")
