# Personal Wardrobe Intelligence Project

## Overview

This project is a web-based machine learning proof-of-concept for personal wardrobe intelligence. The current system allows a user to upload a clothing image and retrieve visually similar garments from a local catalog.

## Problem Addressed

People often struggle to understand what clothing they already own, what styles they repeatedly choose, and what similar items they may want to buy or avoid buying again. This project explores how machine learning can support that process through visual similarity retrieval.

## Proposed Solution

The system uses a retrieval-based approach rather than a traditional classification pipeline.

### Core workflow
1. User uploads a clothing image
2. The system generates an image embedding using CLIP
3. The embedding is compared to catalog embeddings using cosine similarity
4. The system returns the top-k most similar clothing items

The current version focuses on a working web-based proof-of-concept that can later be extended with preference feedback and API-assisted refinement.

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Machine Learning:** CLIP, cosine similarity
- **Data:** Curated subset of the DeepFashion In-Shop Clothes Retrieval dataset
- **Utilities:** NumPy, Pillow, PyTorch

## Repository Structure

```bash
Capstone/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   └── retrieval.py
├── data/        # local only, not tracked in Git
└── artifacts/   # local only, not tracked in Git
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

## Current Limitations

The current MVP uses a sampled local catalog subset, so retrieval quality depends heavily on the quality and consistency of both the catalog and the uploaded query image. The local CLIP baseline performs better on broad clothing categories such as shirts and pants than on more specific garment types such as puffer jackets and cardigans.

## Dataset Reference

This project uses a subset of the **DeepFashion In-Shop Clothes Retrieval** dataset as the local clothing catalog for retrieval experiments.

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

