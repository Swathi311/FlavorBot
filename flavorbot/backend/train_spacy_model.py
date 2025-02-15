import spacy
from spacy.training.example import Example
import json
import os

MODEL_PATH = "./ner_model"

# Load query formats from training_data.json
with open("backend/training_data.json", "r") as f:
    QUERY_FORMATS = json.load(f)

# Load unique ingredients from cached_recipes.json
with open("cached_recipes.json", "r") as f:
    cached_data = json.load(f)

unique_ingredients = cached_data["ingredients"]  # Assuming this has ingredient names

#  Dynamically generate TRAIN_DATA
TRAIN_DATA = []
for ingredient in unique_ingredients:
    for query in QUERY_FORMATS:
        text = query["text"].format(ingredient)  # Insert ingredient into query
        start = query["start_index"]
        end = start + len(ingredient)
        
        TRAIN_DATA.append((text, {"entities": [(start, end, "INGREDIENT")]}))

#  Print sample training data
print(" Generated Training Data Sample:")
for sample in TRAIN_DATA[:5]:  
    print(sample)

#  Load existing model if available, else create a new one
if os.path.exists(MODEL_PATH):
    print(f"Loading existing model from {MODEL_PATH}")
    nlp = spacy.load(MODEL_PATH)
    optimizer = nlp.resume_training()  # Resume training
else:
    print("Creating a new blank model...")
    nlp = spacy.blank("en")
    optimizer = nlp.begin_training()

#  Add the NER pipeline if not present
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

#  Add labels dynamically
for _, annotations in TRAIN_DATA:
    for ent in annotations["entities"]:
        ner.add_label(ent[2])

#  Train only on new data
n_iter = 10  # Reduce iterations for efficiency

for itn in range(n_iter):
    print(f"Iteration {itn + 1}/{n_iter}")
    losses = {}

    for batch in spacy.util.minibatch(TRAIN_DATA, size=10):
        for text, annotations in batch:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], losses=losses, drop=0.3)

    print(losses)

# Save updated model
nlp.to_disk(MODEL_PATH)
print(f"Model updated and saved to {MODEL_PATH}")
