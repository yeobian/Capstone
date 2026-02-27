# src/config.py

# Define the number of classes for the model
NUM_CLASSES = 3

# Define the class names and their corresponding emojis
CLASS_NAMES = {
    0: "👕 Tops",
    1: "👖 Bottoms",
    2: "👟 Shoes"
}

# Path to the directory where models will be saved
MODELS_DIR = "models"

# Default path for the dummy model
DUMMY_MODEL_PATH = "models/dummy_model.pth"
