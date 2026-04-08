import torch
import torch.nn as nn
import timm

class ClothingClassifier(nn.Module):
    """
    Clothing Classifier Network.
    Predicts Category of clothing items.
    """
    def __init__(self, num_classes, backbone='efficientnet_b0', pretrained=True):
        super(ClothingClassifier, self).__init__()
        
        # Modern efficient backbone
        self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0) # num_classes=0 to avoid default head
        
        # Feature dimension from the backbone
        in_features = self.backbone.num_features
        
        # Classification Head
        self.classifier_head = nn.Linear(in_features, num_classes)

    def forward(self, x):
        features = self.backbone(x)
        category_logits = self.classifier_head(features)
        return category_logits
