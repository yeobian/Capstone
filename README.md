# Personal Wardrobe Intelligence Project

## Overview

This project is a **web-based machine learning proof-of-concept** for personal wardrobe intelligence. The current focus is a **visual similarity retrieval system** that allows a user to upload a clothing image and retrieve visually similar garments from a catalog.

The project was refined based on instructor feedback to prioritize a **working web demo** over a multi-platform build. As a result, the primary deliverable is a **web-based application** demonstrating end-to-end image embedding, similarity search, and interactive retrieval.

---

## Problem Statement

People often struggle to understand what clothing they already own, what styles they repeatedly choose, and what similar items they may want to buy or avoid buying again. A simple but useful first step is to allow users to upload a garment image and retrieve visually similar clothing items.

This project explores how machine learning can support that process through embedding-based retrieval.

---

## Current Project Scope

The current version of the project focuses on:

- Uploading a clothing image through a web interface
- Converting the image into an embedding using a pretrained CLIP model
- Comparing the embedding against a catalog of clothing images
- Returning the top-k most similar items
- Planning lightweight user feedback such as **Like / Dislike**
- Laying the foundation for future recommendation and personalization features

---

## Proposed Solution

The system uses a **retrieval-based architecture** rather than a traditional classification pipeline.

### Core workflow
1. User uploads a clothing image
2. The system generates an image embedding using CLIP
3. The embedding is compared to catalog embeddings using cosine similarity
4. The system returns the most similar clothing items
5. User feedback can later be used to adjust future retrieval results

This design keeps the project realistic, demo-ready, and aligned with the capstone requirement for a machine learning–powered web application.

---

## Tech Stack

### Frontend
- **Streamlit** for the web-based user interface

### Backend
- **Python**
- **FastAPI** or lightweight Python integration for retrieval logic

### Machine Learning
- **CLIP** for image embeddings
- **Cosine similarity** for retrieval
- **Faiss** or **ChromaDB** for vector similarity search (optional for MVP)

### Data
- **DeepFashion In-Shop Clothes Retrieval** dataset (subset used as catalog)

### Utilities
- **NumPy**
- **Pandas**
- **Pillow**
- **PyTorch**

---

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