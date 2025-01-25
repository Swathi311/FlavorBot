const admin = require("firebase-admin");

const serviceAccount = require("./serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

const fetchTrainingData = async () => {
  const recipesCollection = db.collection("recipes");
  const snapshot = await recipesCollection.get();

  const trainingData = [];

  snapshot.forEach((doc) => {
    const data = doc.data();
    const description = data.description || "";
    const ingredients = data.ingredients || [];
    const entities = [];

    // Map ingredients to their positions in the description
    ingredients.forEach((ingredient) => {
      const startIdx = description.indexOf(ingredient);
      if (startIdx !== -1) {
        entities.push([startIdx, startIdx + ingredient.length, "INGREDIENT"]);
      }
    });

    // Append formatted training data
    if (entities.length > 0) {
      trainingData.push([description, { entities }]);
    }
  });

  console.log("Training Data:", JSON.stringify(trainingData, null, 2));
  return trainingData;
};

// Export data for spaCy training
fetchTrainingData().then((trainingData) => {
  console.log("Training data ready for spaCy!");
  // Write training data to a file if needed
});
