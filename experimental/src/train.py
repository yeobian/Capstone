import argparse
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from data.dataset import MultiTaskWardrobeDataset, get_transforms
from models.baseline import WardrobeNet
import logging
from tqdm import tqdm
import wandb
import pandas as pd

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
    os.makedirs(args.output_dir, exist_ok=True)
    setup_logging(args.output_dir)
    logging.info(f"Starting training on {device}...")

    # Initialize W&B
    if args.wandb:
        wandb.init(project="wardrobe-intelligence", config=vars(args))

    # Data
    train_dataset = MultiTaskWardrobeDataset(
        csv_file=args.train_csv,
        root_dir=args.data_dir,
        transform=get_transforms(train=True)
    )
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4)
    
    val_dataset = MultiTaskWardrobeDataset(
        csv_file=args.val_csv,
        root_dir=args.data_dir,
        transform=get_transforms(train=False)
    )
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)

    # Model
    model = WardrobeNet(
        num_categories=args.num_categories,
        num_colors=args.num_colors,
        embed_dim=args.embed_dim,
        backbone='efficientnet_b0',
        pretrained=True
    ).to(device)
    
    # Multi-task Loss
    criterion_category = nn.CrossEntropyLoss()
    criterion_color = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    # Training Loop
    best_acc = 0.0
    
    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}")
        for images, cat_labels, color_labels in pbar:
            images = images.to(device)
            cat_labels = cat_labels.to(device)
            color_labels = color_labels.to(device)
            
            optimizer.zero_grad()
            cat_logits, color_logits, _ = model(images)
            
            loss_cat = criterion_category(cat_logits, cat_labels)
            loss_color = criterion_color(color_logits, color_labels)
            
            # Combine losses (can be weighted)
            loss = loss_cat + loss_color
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            pbar.set_postfix({'loss': loss.item()})
            
            if args.wandb:
                wandb.log({"batch_loss": loss.item()})
            
        epoch_loss = running_loss / len(train_dataset)
        logging.info(f"Epoch {epoch+1} Loss: {epoch_loss:.4f}")
        
        # Validation
        model.eval()
        correct_cat = 0
        correct_color = 0
        total = 0
        
        with torch.no_grad():
            for images, cat_labels, color_labels in val_loader:
                images = images.to(device)
                cat_labels = cat_labels.to(device)
                color_labels = color_labels.to(device)
                
                cat_logits, color_logits, _ = model(images)
                
                _, pred_cat = torch.max(cat_logits.data, 1)
                _, pred_color = torch.max(color_logits.data, 1)
                
                total += cat_labels.size(0)
                correct_cat += (pred_cat == cat_labels).sum().item()
                correct_color += (pred_color == color_labels).sum().item()
        
        acc_cat = correct_cat / total
        acc_color = correct_color / total
        avg_acc = (acc_cat + acc_color) / 2
        
        logging.info(f"Epoch {epoch+1} Val Acc - Category: {acc_cat:.4f}, Color: {acc_color:.4f}")
        
        if args.wandb:
            wandb.log({"val_loss": epoch_loss, "val_acc_category": acc_cat, "val_acc_color": acc_color, "epoch": epoch+1})
        
        # Save Best Model
        if avg_acc > best_acc:
            best_acc = avg_acc
            torch.save(model.state_dict(), os.path.join(args.output_dir, 'best_model.pth'))
            logging.info(f"Saved best model with avg acc: {best_acc:.4f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Professional Wardrobe Intelligence Training')
    parser.add_argument('--data_dir', type=str, required=True, help='Path to images directory')
    parser.add_argument('--train_csv', type=str, required=True, help='Path to train annotations CSV')
    parser.add_argument('--val_csv', type=str, required=True, help='Path to val annotations CSV')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--num_categories', type=int, default=3)
    parser.add_argument('--num_colors', type=int, default=5)
    parser.add_argument('--embed_dim', type=int, default=512)
    parser.add_argument('--output_dir', type=str, default='models/')
    parser.add_argument('--wandb', action='store_true', help='Enable Weights & Biases logging')
    
    args = parser.parse_args()
    main(args)
