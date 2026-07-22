# Monuments & Heritage Identifier

An AI-powered Streamlit application that identifies **Indian monuments** from an uploaded image and provides useful visitor information including historical background, opening hours, ticket prices, and a Google Maps link.

---

## Features

- Upload an image of an Indian monument
- Predict the monument using a fine-tuned deep learning model
- Display a short history of the monument
- Show opening hours
- Display ticket prices
- Open the monument directly in Google Maps
- Automatic CLIP zero-shot fallback if the trained model is unavailable

---

## Model Architecture

### Primary Model

- **Backbone:** EfficientNet-B2 (ImageNet pretrained)
- **Input Size:** 224 × 224 RGB
- **Fine-tuning Strategy:**
  - Freeze early layers
  - Fine-tune the last 3 MBConv blocks
  - Replace classifier with a custom classification head
- **Output:** 24 monument classes

### Training Configuration

- Epochs: **15**
- Optimizer: **AdamW**
- Learning Rate Scheduler: **CosineAnnealingLR**
- Label Smoothing: **0.1**

---

## Zero-shot Fallback

If the fine-tuned model weights are unavailable, the application automatically falls back to:

- **CLIP (openai/clip-vit-base-patch32)**

This enables zero-shot monument recognition using only class names without requiring additional training.

---

## Deployment

**Streamlit App**

https://smai-project-dxapenz4fgkfhfmkvv6h5y.streamlit.app

---
