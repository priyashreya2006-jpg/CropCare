
import tensorflow as tf
import numpy as np
import json
from PIL import Image

# Load trained model
model = tf.keras.models.load_model(
    "models/cropcare_mobilenetv2.keras"
)

# Load class labels
with open("models/cropcare_labels.json", "r") as file:
    class_names = json.load(file)

# Image preprocessing
def predict_disease(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    image = np.array(image, dtype=np.float32)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)

    image = np.expand_dims(image, axis=0)

    # Prediction
    predictions = model.predict(image)

    predicted_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_index] * 100

    print("Predicted Disease:", class_names[predicted_index])
    print("Confidence:", round(float(confidence), 2), "%")


# Test image path
image_path = "test_leaf.jpg"

predict_disease(image_path)
