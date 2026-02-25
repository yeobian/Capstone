# -*- coding: utf-8 -*-
import os
import shutil
import random
import logging
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import click

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.option('--split_ratio', default=0.2, help='Ratio of validation set')
def main(input_filepath, output_filepath, split_ratio):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    input_path = Path(input_filepath)
    output_path = Path(output_filepath)
    
    # Create train/val directories
    train_dir = output_path / 'train'
    val_dir = output_path / 'val'
    
    if output_path.exists():
        shutil.rmtree(output_path)
    
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    # Iterate through classes (subdirectories)
    classes = [d for d in input_path.iterdir() if d.is_dir()]
    
    for class_dir in tqdm(classes, desc="Processing classes"):
        class_name = class_dir.name
        
        # Create class subdirectories
        (train_dir / class_name).mkdir(exist_ok=True)
        (val_dir / class_name).mkdir(exist_ok=True)
        
        images = [f for f in class_dir.glob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        random.shuffle(images)
        
        split_idx = int(len(images) * split_ratio)
        val_images = images[:split_idx]
        train_images = images[split_idx:]
        
        # Copy files
        for img in train_images:
            try:
                # Verify image is valid
                with Image.open(img) as i:
                    i.verify() 
                shutil.copy(img, train_dir / class_name / img.name)
            except Exception as e:
                logger.warning(f"Skipping corrupt image {img}: {e}")

        for img in val_images:
            try:
                with Image.open(img) as i:
                    i.verify()
                shutil.copy(img, val_dir / class_name / img.name)
            except Exception as e:
                logger.warning(f"Skipping corrupt image {img}: {e}")

    logger.info(f"Processed data saved to {output_filepath}")

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    main()
