# Personal Wardrobe Intelligence Project

## Overview

This project is a web-based machine learning proof-of-concept for personal wardrobe intelligence. The current focus is a visual similarity retrieval system that allows a user to upload a clothing image and retrieve visually similar garments from a catalog.

The project was refined based on instructor feedback to prioritize a working web demo over a multi-platform build. As a result, the primary deliverable is a web-based application demonstrating end-to-end image embedding, similarity search, and interactive retrieval.

## Problem Statement

People often struggle to understand what clothing they already own, what styles they repeatedly choose, and what similar items they may want to buy or avoid buying again. A simple but useful first step is to allow users to upload a garment image and retrieve visually similar clothing items.

This project explores how machine learning can support that process through embedding-based retrieval.

## Current Project Scope

The current version of the project focuses on:

- Uploading a clothing image through a web interface
- Converting the image into an embedding using a pretrained CLIP model
- Comparing the embedding against a catalog of clothing images
- Returning the top-k most similar items
- Planning lightweight user feedback such as Like / Dislike
- Laying the foundation for future recommendation and personalization features

## Proposed Solution

The system uses a retrieval-based architecture rather than a traditional classification pipeline.

### Core workflow

1. User uploads a clothing image
2. The system generates an image embedding using CLIP
3. The embedding is compared to catalog embeddings using cosine similarity
4. The system returns the most similar clothing items
5. User feedback can later be used to adjust future retrieval results

This design keeps the project realistic, demo-ready, and aligned with the capstone requirement for a machine learning-powered web application.

## Tech Stack

### Frontend
- Streamlit for the web-based user interface

### Backend
- Python
- Lightweight Python-based retrieval pipeline

### Machine Learning
- CLIP for image embeddings
- Cosine similarity for retrieval
- Random sampled local catalog subset for efficient laptop-based experiments

### Data
- DeepFashion In-Shop Clothes Retrieval dataset (curated subset used as the local catalog for retrieval experiments)

### Utilities
- NumPy
- Pandas
- Pillow
- PyTorch

## Repository Structure

```bash
Capstone/
├── app.py                  # Streamlit web application
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and setup instructions
├── src/
│   └── retrieval.py        # Embedding + similarity retrieval logic
├── data/                   # Local dataset storage (not tracked in Git)
├── artifacts/              # Saved embeddings / local outputs
├── models/                 # Model-related files
└── notebooks/              # Optional experimentation / analysis
````

## Steps to Launch the Demo

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add local catalog images

Place catalog images inside:

```bash
data/catalog_images/
```

### 4. Run the web application

```bash
streamlit run app.py
```

## Current Deliverable

The current capstone deliverable is a working web-based proof-of-concept that demonstrates:

* image upload
* CLIP embedding generation
* visual similarity retrieval
* top-k result display

## Current Limitations

The current MVP uses a sampled local catalog subset, so retrieval quality depends heavily on the quality and consistency of both the catalog and the uploaded query image. The local CLIP baseline performs better on broad clothing categories such as shirts and pants than on more specific garment types such as puffer jackets and cardigans. Best results are obtained when the user uploads a clothing image rather than a portrait or unrelated object.

## Hybrid Architecture Direction

The planned next step is a hybrid system that combines:

### Local Open-Source Layer

* Streamlit web app
* Local clothing catalog
* CLIP embeddings
* Cosine similarity retrieval
* Top-k visually similar item display

### API-Assisted Layer

* Preference or intent translation from optional user text
* Style refinement support
* Result explanation or lightweight re-ranking

This hybrid structure is intended to preserve a reproducible local retrieval baseline while adding a practical language-based refinement layer.

## Future Extensions

Possible future work includes:

* like/dislike feedback
* recommend different mode
* text plus image retrieval
* API-assisted preference translation
* preference-aware re-ranking
* future mobile extension after the web demo is stable

## Dataset Reference

This project uses a subset of the **DeepFashion In-Shop Clothes Retrieval** dataset as the local clothing catalog for retrieval experiments.

Original benchmark:

* DeepFashion: In-shop Clothes Retrieval Benchmark

Suggested citation:

```bibtex
@inproceedings{liuLQWTcvpr16DeepFashion,
  author = {Liu, Ziwei and Luo, Ping and Qiu, Shi and Wang, Xiaogang and Tang, Xiaoou},
  title = {DeepFashion: Powering Robust Clothes Recognition and Retrieval with Rich Annotations},
  booktitle = {Proceedings of IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  month = {June},
  year = {2016}
}
```

## Capstone Alignment

This project aligns with the course requirements by:

* addressing a real-world problem
* using machine learning in a meaningful way
* delivering a web-based interactive application
* demonstrating a deployable proof-of-concept
* establishing a foundation for a stronger hybrid image-plus-language system
