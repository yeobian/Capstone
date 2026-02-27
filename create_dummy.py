import torch
import os
import sys

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from models.baseline import ClothingClassifier
from config import NUM_CLASSES, DUMMY_MODEL_PATH

def create_dummy_model():
    print("Creating dummy model...")
    os.makedirs('models', exist_ok=True)
    
    model = ClothingClassifier(num_classes=NUM_CLASSES, pretrained=False)
    
    # Save the initialized weights as a dummy trained model
    torch.save(model.state_dict(), DUMMY_MODEL_PATH)
    print(f"Saved dummy model to {DUMMY_MODEL_PATH}")

if __name__ == '__main__':
    create_dummy_model()
