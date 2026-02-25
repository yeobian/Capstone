# Project Setup & Usage Guide

## 1. Environment Setup

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 2. Data Preparation

Organize your dataset in the `data/raw` folder:
```
data/raw/
  train/
    tops/
      img1.jpg
      ...
    bottoms/
    shoes/
  val/
    tops/
    ...
```

## 3. Training the Model

Run the training script:
```bash
python src/train.py \
    --data_dir data/raw \
    --epochs 20 \
    --batch_size 32 \
    --num_classes 10 \
    --output_dir models/
```

## 4. Evaluation

(Coming soon: Evaluation metrics and visualization notebook)
