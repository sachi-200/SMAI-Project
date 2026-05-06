# T12.1 – Monuments & Heritage Identifier: Top monuments fine-tuned

A tourist points their phone at an Indian monument; the app names it, gives history, opening hours, ticket prices, and a Google Maps link.

## Files

| File | Purpose |
|------|---------|
| `training_notebook.ipynb` | Training script (run on Kaggle GPU) |
| `app.py` | Streamlit web app |
| `build_metadata.py` | One-time Wikipedia metadata scraper |
| `requirements.txt` | Python dependencies |

## Model Architecture

- **Backbone:** EfficientNet-B2 (ImageNet pretrained)
- **Fine-tuning:** Last 3 MBConv blocks + custom classifier head
- **Input:** 224×224 RGB images
- **Output:** 24 monument classes
- **Training:** 15 epochs, AdamW + CosineAnnealingLR, label smoothing 0.1

## Zero-shot Fallback

If the trained model is unavailable, the app falls back to **CLIP (openai/clip-vit-base-patch32)** zero-shot classification.

## Skills Used

- Transfer learning / fine-tuning (EfficientNet-B2)
- CLIP zero-shot classification
- Wikipedia API scraping for metadata
- Streamlit for deployment

## Deployment Link

smai-project-dxapenz4fgkfhfmkvv6h5y.streamlit.app
