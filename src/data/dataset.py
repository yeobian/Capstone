import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class MultiTaskWardrobeDataset(Dataset):
    """
    Professional Multi-Task Dataset.
    Loads images and multi-label metadata from a CSV file.
    Expects metadata format: image_path, category_id, color_id
    """
    def __init__(self, csv_file, root_dir, transform=None):
        self.annotations = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform
        
    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.annotations.iloc[idx, 0])
        image = Image.open(img_name).convert('RGB')
        
        category_label = int(self.annotations.iloc[idx, 1])
        color_label = int(self.annotations.iloc[idx, 2])
        
        if self.transform:
            image = self.transform(image)
            
        return image, category_label, color_label

def get_transforms(train=True):
    """
    Advanced Data Augmentation Pipeline to handle noisy real-world data (wrinkles, lighting)
    """
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    
    if train:
        return transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1)),
            transforms.ToTensor(),
            normalize,
        ])
    else:
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize,
        ])
