
import json
import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_PATH = "models/cropcare_mobilenetv2.keras"
LABELS_PATH = "models/cropcare_labels.json"

IMG_SIZE = (224, 224)

# Load model once
model = tf.keras.models.load_model(MODEL_PATH)


# Load disease labels
def load_labels():

    with open(LABELS_PATH, "r") as file:
        labels = json.load(file)

    return labels


labels = load_labels()


# Prepare uploaded image
def prepare_image(image_path):

    image = Image.open(image_path).convert("RGB")

    image = image.resize(IMG_SIZE)

    image_array = np.array(image, dtype=np.float32)

    image_array = (image_array / 127.5) - 1.0

    image_array = np.expand_dims(image_array, axis=0)

    return image_array


# Predict plant disease
def predict_disease(image_path):

    image_array = prepare_image(image_path)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))

    disease_name = labels[predicted_index]

    confidence = float(predictions[0][predicted_index]) * 100

    return disease_name, confidence

