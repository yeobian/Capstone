import torch
import torch.nn as nn
import timm

class WardrobeNet(nn.Module):
    """
    Multi-Task Learning Network for Wardrobe Intelligence.
    Predicts Category, Color, and outputs a 512-D Embedding for Similarity Search.
    """
    def __init__(self, num_categories=10, num_colors=10, embed_dim=512, backbone='efficientnet_b0', pretrained=True):
        super(WardrobeNet, self).__init__()
        
        # Modern efficient backbone
        self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0)
        
        # Feature dimension from the backbone
        in_features = self.backbone.num_features
        
        # Shared Embedding Space (used for FAISS/Similarity)
        self.embedding = nn.Sequential(
            nn.Linear(in_features, embed_dim),
            nn.BatchNorm1d(embed_dim),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        
        # Task 1: Category Head (e.g., Tops, Bottoms, Shoes)
        self.category_head = nn.Linear(embed_dim, num_categories)
        
        # Task 2: Color/Pattern Head (e.g., Red, Blue, Striped)
        self.color_head = nn.Linear(embed_dim, num_colors)

    def forward(self, x):
        features = self.backbone(x)
        embeddings = self.embedding(features)
        
        category_logits = self.category_head(embeddings)
        color_logits = self.color_head(embeddings)
        
        # L2 Normalize embeddings for cosine similarity later
        norm_embeddings = nn.functional.normalize(embeddings, p=2, dim=1)
        
        return category_logits, color_logits, norm_embeddings
