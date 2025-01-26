import spacy
from spacy.training.example import Example


TRAIN_DATA = [
    # Basic ingredient mentions
    ("Do you have a recipe with Paneer and Spinach?", {"entities": [(26, 32, "INGREDIENT"), (37, 44, "INGREDIENT")]}),
    ("I need a dish that uses Chicken and Garlic.", {"entities": [(24, 31, "INGREDIENT"), (36, 42, "INGREDIENT")]}),

    # Substitutions and alternative suggestions
    ("What can I use instead of Butter for baking?", {"entities": [(26, 32, "INGREDIENT")]}),
    ("Can I replace Eggs with Bananas in this recipe?", {"entities": [(14, 18, "INGREDIENT"), (24, 31, "INGREDIENT")]}),
    ("Suggest a dairy-free alternative to Milk.", {"entities": [(35, 39, "INGREDIENT")]}),

    # Recipe searches
    ("Show me a recipe for Chocolate Cake.", {"entities": [(19, 28, "INGREDIENT")]}),
    ("Find recipes with Potatoes and Peas.", {"entities": [(18, 26, "INGREDIENT"), (31, 35, "INGREDIENT")]}),
    ("Can you give me a Mango smoothie recipe?", {"entities": [(20, 25, "INGREDIENT")]}),

    # Complex ingredient mentions in context
    ("Can you give me a vegetarian recipe with Lentils and Tofu?", {"entities": [(41, 48, "INGREDIENT"), (53, 57, "INGREDIENT")]}),
    ("What can I make with Strawberries, Blueberries, and Cream?", {"entities": [(19, 31, "INGREDIENT"), (33, 44, "INGREDIENT"), (50, 55, "INGREDIENT")]}),
    ("Do you know a recipe that combines Mushrooms and Broccoli?", {"entities": [(32, 41, "INGREDIENT"), (46, 54, "INGREDIENT")]}),

    # Instructions with ingredients
    ("Add Sugar and Butter to the mixture.", {"entities": [(5, 10, "INGREDIENT"), (15, 21, "INGREDIENT")]}),
    ("Marinate the Chicken with Yogurt and Spices.", {"entities": [(15, 22, "INGREDIENT"), (28, 34, "INGREDIENT")]}),
    ("Stir in the Tomato paste and season with Salt.", {"entities": [(12, 18, "INGREDIENT"), (37, 41, "INGREDIENT")]}),

    # Negative examples (to avoid overfitting)
    ("Can you recommend a non-stick pan?", {"entities": []}),
    ("What's the best way to sharpen a knife?", {"entities": []}),
    ("Do I need a specific kind of skillet for this dish?", {"entities": []}),

    # Regional cuisine examples
    ("How do I make a South Indian recipe with Tamarind?", {"entities": [(40, 48, "INGREDIENT")]}),
    ("What ingredients are needed for a Punjabi Chole?", {"entities": [(44, 49, "INGREDIENT")]}),
    ("Can you suggest an Italian pasta recipe with Basil?", {"entities": [(45, 50, "INGREDIENT")]}),

    # Questions about cooking techniques
    ("Can I sauté Onions in Olive oil?", {"entities": [(10, 16, "INGREDIENT"), (20, 29, "INGREDIENT")]}),
    ("Is it okay to fry Potatoes in Coconut oil?", {"entities": [(19, 27, "INGREDIENT"), (31, 42, "INGREDIENT")]}),
    ("What spice blend works best for grilling Lamb?", {"entities": [(42, 46, "INGREDIENT")]}),

    # Substitutes or dietary concerns
    ("What's a gluten-free substitute for Wheat Flour?", {"entities": [(33, 44, "INGREDIENT")]}),
    ("I need a sugar-free recipe for people avoiding Sugar.", {"entities": [(53, 58, "INGREDIENT")]}),
    ("What can I use instead of Butter to make it vegan?", {"entities": [(26, 32, "INGREDIENT")]}),

    # Desserts and baked goods
    ("Can you give me a recipe for Carrot Cake?", {"entities": [(28, 33, "INGREDIENT")]}),
    ("How do I make a Cheesecake with Cream Cheese?", {"entities": [(34, 40, "INGREDIENT"), (46, 57, "INGREDIENT")]}),
    ("What is the best way to bake with Almond Flour?", {"entities": [(34, 46, "INGREDIENT")]}),

    # Drinks and smoothies
    ("Give me a smoothie recipe with Bananas and Honey.", {"entities": [(31, 38, "INGREDIENT"), (43, 48, "INGREDIENT")]}),
    ("How do I prepare a Green Tea latte?", {"entities": [(19, 28, "INGREDIENT")]}),
    ("What are the ingredients for a Mango Lassi?", {"entities": [(36, 41, "INGREDIENT")]}),
]




# Create a blank NLP model
nlp = spacy.blank("en")

# Add the NER pipeline if not already added
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add labels to the NER pipeline
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])  # Add the label (e.g., "INGREDIENT")

# Create the optimizer
optimizer = nlp.begin_training()

# Number of iterations
n_iter = 30

# Training loop
for itn in range(n_iter):
    print(f"Iteration {itn + 1}/{n_iter}")
    losses = {}

    for batch in spacy.util.minibatch(TRAIN_DATA, size=2):
        for text, annotations in batch:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], losses=losses, drop=0.1)
    print(losses)


# Save the trained model
nlp.to_disk("./ner_model")
print("Model saved to ./ner_model")
