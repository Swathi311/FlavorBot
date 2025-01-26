from spacy.training import offsets_to_biluo_tags
from spacy.lang.en import English

# Replace with your actual training data
TRAIN_DATA = [
    ("Paneer Makhana curry is delicious.", {"entities": [(0, 6, "INGREDIENT"), (7, 14, "INGREDIENT")]}),
    ("Sugar, milk, and almonds are great ingredients.", {"entities": [(0, 5, "INGREDIENT"), (7, 11, "INGREDIENT"), (17, 24, "INGREDIENT")]}),
    # Add more training examples here
]

def validate_data(training_data):
    nlp = English()
    for i, (text, annotations) in enumerate(training_data):
        try:
            doc = nlp.make_doc(text)
            tags = offsets_to_biluo_tags(doc, annotations["entities"])
            print(f"Example {i + 1} is valid.")
        except Exception as e:
            print(f"Example {i + 1} has an error: {e}")
            print(f"Text: {text}")
            print(f"Annotations: {annotations}")

if __name__ == "__main__":
    validate_data(TRAIN_DATA)
