import spacy

# Load the trained model
nlp = spacy.load('./ner_model')

# Test the model with a new text
text = "Paneer Makhana Gulgule Chaat Recipe is a chaat made with paneer and makhana."
doc = nlp(text)

# Print out the tokens and entities
print("Tokens:")
for token in doc:
    print(f"Token: {token.text}, Index: {token.idx}")

print("\nEntities:")
for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}, Span: {ent.start_char}-{ent.end_char}")
