import spacy

MODEL_PATH = "./ner_model"

try:
    nlp = spacy.load(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")


print("Pipeline components:", nlp.pipe_names)

test_text = "Give me a Mango smoothie recipe."
doc = nlp(test_text)

print("\nEntities:")
for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}, Start: {ent.start_char}, End: {ent.end_char}")

print("\nTokens with Entity Tags:")
for token in doc:
    print(f"Token: {token.text}, Tag: {token.ent_type_}") 