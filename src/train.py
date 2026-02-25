import argparse
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from data.dataset import WardrobeDataset, get_transforms
from models.baseline import ClothingClassifier
import logging
from tqdm import tqdm

def setup_logging(log_dir):
    logging.basicConfig(
        filename=os.path.join(log_dir, 'training.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def main(args):
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    setup_logging('models/')
    logging.info(f"Starting training on {device}...")

    # Data
    train_dataset = WardrobeDataset(
        data_dir=os.path.join(args.data_dir, 'train'),
        transform=get_transforms(train=True)
    )
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4)
    
    val_dataset = WardrobeDataset(
        data_dir=os.path.join(args.data_dir, 'val'),
        transform=get_transforms(train=False)
    )
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)

    # Model
    model = ClothingClassifier(num_classes=args.num_classes, pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    # Training Loop
    best_acc = 0.0
    
    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}"):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_loss = running_loss / len(train_dataset)
        logging.info(f"Epoch {epoch+1} Loss: {epoch_loss:.4f}")
        
        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        acc = correct / total
        logging.info(f"Epoch {epoch+1} Validation Accuracy: {acc:.4f}")
        
        # Save Best Model
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), os.path.join(args.output_dir, 'best_model.pth'))
            logging.info(f"Saved best model with acc: {best_acc:.4f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Wardrobe Classifier')
    parser.add_argument('--data_dir', type=str, required=True, help='Path to data directory containing train/val folders')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--num_classes', type=int, default=10)
    parser.add_argument('--output_dir', type=str, default='models/')
    
    args = parser.parse_args()
    main(args)
