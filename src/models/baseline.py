import torch.nn as nn
import torchvision.models as models

class ClothingClassifier(nn.Module):
    """
    ResNet-based classifier for clothing items.
    """
    def __init__(self, num_classes=10, pretrained=True):
        super(ClothingClassifier, self).__init__()
        
        # Load Pretrained ResNet-50
        self.backbone = models.resnet50(pretrained=pretrained)
        
        # Replace the final FC layer
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)
        
        # Optional: Add dropout for regularization
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        return self.backbone(x)
