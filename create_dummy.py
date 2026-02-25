import torch
import os
import sys

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from models.baseline import ClothingClassifier

def create_dummy_model():
    print("Creating dummy model...")
    os.makedirs('models', exist_ok=True)
    
    # We have 3 classes: tops, bottoms, shoes (based on SETUP.md)
    model = ClothingClassifier(num_classes=3, pretrained=False)
    
    # Save the initialized weights as a dummy trained model
    torch.save(model.state_dict(), 'models/dummy_model.pth')
    print("Saved dummy_model.pth to models/")

if __name__ == '__main__':
    create_dummy_model()
