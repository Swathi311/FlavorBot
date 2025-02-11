import spacy
from spacy.training.example import Example
import json

# Load cached ingredient & recipe data
with open("cached_recipes.json", "r") as f:
    cached_data = json.load(f)

unique_ingredients = cached_data["ingredients"]

# Create dynamic TRAIN_DATA
TRAIN_DATA = []

for ingredient in unique_ingredients:
    TRAIN_DATA.extend([
        (f"Show me recipes with {ingredient}", {"entities": [(21, 21 + len(ingredient), "INGREDIENT")]}),
        (f"I want a dish with {ingredient}", {"entities": [(19, 19 + len(ingredient), "INGREDIENT")]}),
        (f"What can I cook using {ingredient}?", {"entities": [(22, 22 + len(ingredient), "INGREDIENT")]}),
        (f"How do I prepare a meal with {ingredient}?", {"entities": [(29, 29 + len(ingredient), "INGREDIENT")]}),
        (f"I need a recipe with {ingredient}", {"entities": [(21, 21 + len(ingredient), "INGREDIENT")]}),
        (f"Suggest something to cook with {ingredient}", {"entities": [(31, 31 + len(ingredient), "INGREDIENT")]}),
    ])

print("Training Data Sample:")
for sample in TRAIN_DATA[:10]:  # Print first 5 examples
    print(sample)

# Create a blank NLP model
nlp = spacy.blank("en")

# Add the NER pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add labels to the NER pipeline
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Create the optimizer
optimizer = nlp.begin_training()

# Number of iterations
n_iter = 30

# Training loop
for itn in range(n_iter):
    print(f"Iteration {itn + 1}/{n_iter}")
    losses = {}

    for batch in spacy.util.minibatch(TRAIN_DATA, size=10):  # Larger batch size for efficiency
        for text, annotations in batch:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], losses=losses, drop=0.3)  # Dropout increased to 0.2 to prevent overfitting

    print(losses)

# Save the trained model
nlp.to_disk("./ner_model")
print("Model saved to ./ner_model")
