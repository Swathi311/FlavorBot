import spacy
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags
from spacy.lang.en import English

# Sample training data
TRAIN_DATA = [
    ("Paneer Makhana Gulgule Chaat Recipe is a chaat made with paneer and makhana.", {"entities": [(0, 6, "INGREDIENT"), (27, 33, "INGREDIENT")]}),
    ("The recipe requires sugar, milk, and almonds.", {"entities": [(22, 27, "INGREDIENT"), (29, 33, "INGREDIENT"), (39, 46, "INGREDIENT")]}),
    ("Prepare the dish by adding tomatoes, onions, and garlic.", {"entities": [(31, 38, "INGREDIENT"), (40, 46, "INGREDIENT"), (49, 55, "INGREDIENT")]}),
    ("For a dessert, use chocolate, cream, and butter.", {"entities": [(18, 26, "INGREDIENT"), (28, 33, "INGREDIENT"), (36, 42, "INGREDIENT")]}),
]


# Function to clean and validate training data
def clean_training_data(data):
    """Removes overlapping or misaligned entities from training data."""
    cleaned_data = []
    nlp = English()  # Use spaCy's English model for tokenization
    for text, annotations in data:
        try:
            doc = nlp.make_doc(text)
            # Validate entity alignment
            biluo_tags = offsets_to_biluo_tags(doc, annotations["entities"])
            valid_entities = annotations["entities"]
        except ValueError as e:
            print(f"Skipping invalid data: {text} - {annotations} ({e})")
            valid_entities = []  # Skip problematic entities
        if valid_entities:
            cleaned_data.append((text, {"entities": valid_entities}))
    print("Cleaned training data:", cleaned_data)
    return cleaned_data

# Clean the training data
TRAIN_DATA = clean_training_data(TRAIN_DATA)

# Function to train the spaCy NER model
def train_model(data, model=None, output_dir=None, n_iter=30):
    """Train an NER model using spaCy."""
    # Load an existing model or create a blank model
    if model is not None:
        nlp = spacy.load(model)  # Load existing spaCy model
        print(f"Loaded model '{model}'")
    else:
        nlp = spacy.blank("en")  # Create blank English model
        print("Created blank 'en' model")

    # Add NER pipeline if not already present
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    # Add labels to the NER pipeline
    for _, annotations in data:
        for ent in annotations["entities"]:
            ner.add_label(ent[2])

    # Train the model
    optimizer = nlp.begin_training()
    for i in range(n_iter):
        print(f"Iteration {i + 1}/{n_iter}")
        losses = {}
        for text, annotations in data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.5, losses=losses)
        print(f"Losses: {losses}")

    # Save the model to the specified output directory
    if output_dir is not None:
        nlp.to_disk(output_dir)
        print(f"Model saved to {output_dir}")

# Train the model and save it
if __name__ == "__main__":
    OUTPUT_DIR = "./ner_model"  # Path to save the trained model
    train_model(TRAIN_DATA, model=None, output_dir=OUTPUT_DIR, n_iter=10)
