# # =============================================================
# # T12.1 – Monuments & Heritage Identifier
# # Streamlit App  (app.py)
# # Deploy on: Streamlit Community Cloud or HuggingFace Spaces
# # =============================================================
# # requirements.txt:
# #   streamlit>=1.33
# #   torch>=2.2
# #   torchvision>=0.17
# #   Pillow>=10
# #   transformers>=4.40   # for CLIP fallback
# #   requests>=2.31
# #   wikipedia-api>=0.6
# # =============================================================

# import json, os, urllib.parse
# import streamlit as st
# import torch
# import torch.nn as nn
# from torchvision import transforms, models
# from PIL import Image
# import requests

# # ── Page config ──────────────────────────────────────────────
# st.set_page_config(
#     page_title="Indian Monuments Identifier",
#     page_icon="🏛️",
#     layout="centered",
# )

# # ── Monument metadata (cached JSON) ──────────────────────────
# # Run once: python build_metadata.py  →  monument_metadata.json
# # Or use the inline dict below as fallback.

# MONUMENT_META = {
#     "Taj Mahal": {
#         "history": "Built between 1631–1648 by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. A UNESCO World Heritage Site and one of the Seven Wonders of the World.",
#         "hours": "Sunrise to Sunset (closed on Fridays)",
#         "ticket": "₹50 (Indian) | ₹1,100 (Foreign) | Free under 15 yrs",
#         "location": "Agra, Uttar Pradesh",
#         "lat": 27.1751, "lng": 78.0421,
#     },
#     "Red Fort": {
#         "history": "Commissioned by Mughal Emperor Shah Jahan in 1638, it served as the main residence of the Mughal Emperors for nearly 200 years.",
#         "hours": "9:30 AM – 4:30 PM (closed Mondays)",
#         "ticket": "₹35 (Indian) | ₹500 (Foreign)",
#         "location": "Delhi",
#         "lat": 28.6562, "lng": 77.2410,
#     },
#     "Qutub Minar": {
#         "history": "A 73-metre tall minaret built in 1193 by Qutub ud-Din Aibak. It is the world's tallest brick minaret and a UNESCO World Heritage Site.",
#         "hours": "Sunrise to Sunset (all days)",
#         "ticket": "₹35 (Indian) | ₹550 (Foreign)",
#         "location": "New Delhi",
#         "lat": 28.5244, "lng": 77.1855,
#     },
#     "Humayun's Tomb": {
#         "history": "Built in 1570, it was the first garden-tomb on the Indian subcontinent and inspired several later monuments including the Taj Mahal.",
#         "hours": "Sunrise to Sunset",
#         "ticket": "₹35 (Indian) | ₹550 (Foreign)",
#         "location": "New Delhi",
#         "lat": 28.5933, "lng": 77.2507,
#     },
#     "Hawa Mahal": {
#         "history": "Built in 1799 by Maharaja Sawai Pratap Singh of Jaipur. The 'Palace of Winds' has 953 windows designed to allow royal women to observe street life.",
#         "hours": "9:00 AM – 5:00 PM",
#         "ticket": "₹50 (Indian) | ₹200 (Foreign)",
#         "location": "Jaipur, Rajasthan",
#         "lat": 26.9239, "lng": 75.8267,
#     },
#     "India Gate": {
#         "history": "A war memorial built in 1931 dedicated to 82,000 soldiers of the British Indian Army who died in World War I and the Third Anglo-Afghan War.",
#         "hours": "Open 24 hours",
#         "ticket": "Free",
#         "location": "New Delhi",
#         "lat": 28.6129, "lng": 77.2295,
#     },
#     "Mysore Palace": {
#         "history": "The official residence of the Wadiyar dynasty, it was rebuilt between 1897 and 1912. It is one of India's most visited monuments.",
#         "hours": "10:00 AM – 5:30 PM",
#         "ticket": "₹70 (Indian) | ₹200 (Foreign)",
#         "location": "Mysuru, Karnataka",
#         "lat": 12.3052, "lng": 76.6552,
#     },
#     "Konark Sun Temple": {
#         "history": "A 13th-century Sun temple at Konark in Odisha. Designed as a giant chariot with 12 pairs of stone wheels, it is a UNESCO World Heritage Site.",
#         "hours": "6:00 AM – 8:00 PM",
#         "ticket": "₹40 (Indian) | ₹600 (Foreign)",
#         "location": "Konark, Odisha",
#         "lat": 19.8876, "lng": 86.0945,
#     },
#     "Meenakshi Temple": {
#         "history": "A historic Hindu temple dedicated to Parvati (Meenakshi) and Shiva (Sundareswarar). The temple has been rebuilt in the 17th century on an ancient site.",
#         "hours": "5:00 AM – 12:30 PM & 4:00 PM – 9:30 PM",
#         "ticket": "Free (camera fee: ₹50)",
#         "location": "Madurai, Tamil Nadu",
#         "lat": 9.9195, "lng": 78.1193,
#     },
#     "Charminar": {
#         "history": "Built in 1591 by Muhammad Quli Qutb Shah to commemorate the founding of Hyderabad. Its name means 'Four Minarets' in Urdu.",
#         "hours": "9:30 AM – 5:30 PM (closed Fridays)",
#         "ticket": "₹25 (Indian) | ₹300 (Foreign)",
#         "location": "Hyderabad, Telangana",
#         "lat": 17.3616, "lng": 78.4747,
#     },
#     "Amber Fort": {
#         "history": "A fort-palace complex atop a hill in Amer, Rajasthan, built from 1592 onward by Raja Man Singh I. Known for its artistic Hindu-Mughal architecture.",
#         "hours": "8:00 AM – 5:30 PM (night tour: 7 PM – 10 PM)",
#         "ticket": "₹100 (Indian) | ₹500 (Foreign)",
#         "location": "Amer, Rajasthan",
#         "lat": 26.9855, "lng": 75.8513,
#     },
#     "Victoria Memorial": {
#         "history": "Built between 1906 and 1921 in memory of Queen Victoria, it is a marble museum and tourist destination in Kolkata.",
#         "hours": "10:00 AM – 5:00 PM (closed Mondays)",
#         "ticket": "₹30 (Indian) | ₹500 (Foreign)",
#         "location": "Kolkata, West Bengal",
#         "lat": 22.5448, "lng": 88.3426,
#     },
#     "Gateway of India": {
#         "history": "An arch-monument built in Mumbai to commemorate the landing of King George V and Queen Mary in 1911. Completed in 1924.",
#         "hours": "Open 24 hours",
#         "ticket": "Free",
#         "location": "Mumbai, Maharashtra",
#         "lat": 18.9220, "lng": 72.8347,
#     },
#     "Ajanta Caves": {
#         "history": "A series of 30 rock-cut Buddhist cave monuments in Maharashtra dating back to the 2nd century BCE. A UNESCO World Heritage Site famous for murals and sculptures.",
#         "hours": "9:00 AM – 5:30 PM (closed Mondays)",
#         "ticket": "₹40 (Indian) | ₹600 (Foreign)",
#         "location": "Aurangabad, Maharashtra",
#         "lat": 20.5519, "lng": 75.7033,
#     },
#     "Ellora Caves": {
#         "history": "A UNESCO World Heritage Site featuring 100 cave temples and monasteries cut from basaltic rock between the 6th and 11th centuries CE, showcasing Hindu, Buddhist, and Jain art.",
#         "hours": "6:00 AM – 6:00 PM (closed Tuesdays)",
#         "ticket": "₹40 (Indian) | ₹600 (Foreign)",
#         "location": "Aurangabad, Maharashtra",
#         "lat": 20.0268, "lng": 75.1788,
#     },
#     "Sanchi Stupa": {
#         "history": "The oldest stone structure in India, the Great Stupa at Sanchi was originally commissioned by Emperor Ashoka in the 3rd century BCE.",
#         "hours": "Sunrise to Sunset",
#         "ticket": "₹30 (Indian) | ₹500 (Foreign)",
#         "location": "Sanchi, Madhya Pradesh",
#         "lat": 23.4798, "lng": 77.7395,
#     },
#     "Fatehpur Sikri": {
#         "history": "A city founded in 1571 by the Mughal Emperor Akbar and served as his capital for 14 years. A UNESCO World Heritage Site.",
#         "hours": "Sunrise to Sunset",
#         "ticket": "₹50 (Indian) | ₹610 (Foreign)",
#         "location": "Agra, Uttar Pradesh",
#         "lat": 27.0945, "lng": 77.6632,
#     },
#     "Mahabalipuram": {
#         "history": "A group of 7th and 8th century CE monuments and temples built by Pallava kings. A UNESCO World Heritage Site known for its Shore Temple.",
#         "hours": "6:00 AM – 6:00 PM",
#         "ticket": "₹40 (Indian) | ₹600 (Foreign)",
#         "location": "Chengalpattu, Tamil Nadu",
#         "lat": 12.6269, "lng": 80.1927,
#     },
# }

# # Try loading from JSON file (generated by scraper)
# META_FILE = "monument_metadata.json"
# if os.path.exists(META_FILE):
#     with open(META_FILE) as f:
#         MONUMENT_META.update(json.load(f))

# # ── Load model ────────────────────────────────────────────────
# MODEL_FILE   = "monument_classifier.pth"
# CLASSES_FILE = "classes.json"

# @st.cache_resource
# def load_model():
#     if not os.path.exists(MODEL_FILE) or not os.path.exists(CLASSES_FILE):
#         return None, None

#     with open(CLASSES_FILE) as f:
#         class_names = json.load(f)

#     device = torch.device("cpu")

#     # Rebuild same architecture used in training
#     m = models.efficientnet_b2(weights=None)
#     in_features = m.classifier[1].in_features
#     m.classifier = nn.Sequential(
#         nn.Dropout(p=0.4),
#         nn.Linear(in_features, 512),
#         nn.ReLU(),
#         nn.Dropout(p=0.3),
#         nn.Linear(512, len(class_names)),
#     )
#     ckpt = torch.load(MODEL_FILE, map_location=device)
#     m.load_state_dict(ckpt["model_state_dict"])
#     m.eval()
#     return m, class_names

# model, class_names = load_model()

# # ── Inference helpers ─────────────────────────────────────────
# INF_TF = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
# ])

# def predict(img: Image.Image):
#     tensor = INF_TF(img.convert("RGB")).unsqueeze(0)
#     with torch.no_grad():
#         logits = model(tensor)
#         probs  = torch.softmax(logits, dim=1)[0]
#     top5_probs, top5_idx = probs.topk(5)
#     top5 = [(class_names[i], float(p)) for i, p in zip(top5_idx, top5_probs)]
#     return top5

# def google_maps_url(name, lat=None, lng=None):
#     if lat and lng:
#         return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
#     q = urllib.parse.quote(f"{name} monument India")
#     return f"https://www.google.com/maps/search/?api=1&query={q}"

# # ── CLIP zero-shot fallback ───────────────────────────────────
# @st.cache_resource
# def load_clip():
#     try:
#         from transformers import CLIPProcessor, CLIPModel
#         clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
#         clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
#         return clip_model, clip_proc
#     except Exception:
#         return None, None

# CLIP_LABELS = [
#     "Taj Mahal", "Red Fort", "Qutub Minar", "Humayun's Tomb",
#     "Hawa Mahal", "India Gate", "Mysore Palace", "Konark Sun Temple",
#     "Meenakshi Temple", "Charminar", "Amber Fort", "Victoria Memorial",
#     "Gateway of India", "Ajanta Caves", "Ellora Caves",
#     "Sanchi Stupa", "Fatehpur Sikri", "Mahabalipuram",
# ]

# def predict_clip(img: Image.Image):
#     clip_model, clip_proc = load_clip()
#     if clip_model is None:
#         return None
#     texts = [f"a photo of {n}" for n in CLIP_LABELS]
#     inputs = clip_proc(text=texts, images=img, return_tensors="pt", padding=True)
#     with torch.no_grad():
#         out    = clip_model(**inputs)
#         probs  = out.logits_per_image.softmax(dim=1)[0]
#     top5_probs, top5_idx = probs.topk(5)
#     return [(CLIP_LABELS[i], float(p)) for i, p in zip(top5_idx, top5_probs)]

# # ── UI ────────────────────────────────────────────────────────
# st.title("🏛️ Indian Monuments & Heritage Identifier")
# st.caption("Upload a photo of an Indian monument to get its name, history, visiting hours, ticket prices, and location.")

# # Sidebar: mode info
# with st.sidebar:
#     st.header("ℹ️ About")
#     if model:
#         st.success("Fine-tuned EfficientNet-B2 loaded ✅")
#     else:
#         st.warning("Model file not found – using CLIP zero-shot fallback.")
#     st.markdown("**Dataset:** 24 Indian monuments (~3.5k images)")
#     st.markdown("**Task:** T12.1 – Monuments & Heritage Identifier")
#     st.markdown("---")
#     st.markdown("Built with PyTorch + Streamlit")

# uploaded = st.file_uploader("Upload a monument photo", type=["jpg", "jpeg", "png", "webp"])

# if uploaded:
#     img = Image.open(uploaded).convert("RGB")
#     st.image(img, caption="Uploaded Image", use_column_width=True)

#     with st.spinner("Identifying monument…"):
#         if model:
#             top5 = predict(img)
#         else:
#             top5 = predict_clip(img)

#     if not top5:
#         st.error("Could not run inference. Please ensure model or CLIP is available.")
#         st.stop()

#     name, confidence = top5[0]

#     # ── Result card ──────────────────────────────────────────
#     st.divider()
#     col1, col2 = st.columns([2, 1])
#     with col1:
#         st.subheader(f"🏆 {name}")
#         st.metric("Confidence", f"{confidence*100:.1f}%")
#     with col2:
#         meta = MONUMENT_META.get(name, {})
#         if meta.get("lat"):
#             maps_url = google_maps_url(name, meta["lat"], meta["lng"])
#         else:
#             maps_url = google_maps_url(name)
#         st.link_button("📍 Open in Google Maps", maps_url, use_container_width=True)

#     # ── Metadata ─────────────────────────────────────────────
#     if meta:
#         st.markdown("### 📖 History")
#         st.info(meta.get("history", "No history available."))

#         col_a, col_b, col_c = st.columns(3)
#         col_a.metric("📍 Location",  meta.get("location", "—"))
#         col_b.metric("🕐 Hours",     meta.get("hours",    "—"))
#         col_c.metric("🎟️ Ticket",   meta.get("ticket",   "—"))
#     else:
#         st.warning(f"Metadata for **{name}** not found in the local database. "
#                    "Consider running the Wikipedia scraper to enrich it.")

#     # ── Top-5 bar chart ──────────────────────────────────────
#     with st.expander("Show top-5 predictions"):
#         import pandas as pd
#         df = pd.DataFrame(top5, columns=["Monument", "Probability"])
#         df["Probability (%)"] = (df["Probability"] * 100).round(2)
#         st.bar_chart(df.set_index("Monument")["Probability (%)"])

#     # ── Feedback ─────────────────────────────────────────────
#     st.divider()
#     st.markdown("**Was this correct?**")
#     cols = st.columns(3)
#     if cols[0].button("✅ Yes"):
#         st.success("Thank you for the feedback!")
#     if cols[1].button("❌ No"):
#         correct = st.text_input("What is the correct monument?")
#         if correct:
#             st.info(f"Logged: '{correct}'. Thank you!")
#     if cols[2].button("🤷 Not sure"):
#         st.info("No problem!")

# else:
#     st.markdown("""
#     ### How it works
#     1. **Upload** a photo of any Indian monument.
#     2. The model **identifies** the monument using a fine-tuned EfficientNet-B2.
#     3. You get **history**, **visiting hours**, **ticket prices** and a **Google Maps** link.

#     > **Supported monuments (24):** Taj Mahal, Red Fort, Qutub Minar, Hawa Mahal,
#     > India Gate, Mysore Palace, Konark Sun Temple, Meenakshi Temple, Charminar,
#     > Amber Fort, Victoria Memorial, Gateway of India, Ajanta Caves, Ellora Caves,
#     > Sanchi Stupa, Fatehpur Sikri, Mahabalipuram, Humayun's Tomb, and more.
#     """)

# =============================================================
# T12.1 – Monuments & Heritage Identifier
# Streamlit App  (app.py)
# Deploy on: Streamlit Community Cloud or HuggingFace Spaces
# =============================================================
# requirements.txt:
#   streamlit>=1.33
#   torch>=2.2
#   torchvision>=0.17
#   Pillow>=10
#   transformers>=4.40   # for CLIP fallback
#   requests>=2.31
#   wikipedia-api>=0.6
# =============================================================

import json, os, urllib.parse
import streamlit as st
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import requests

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Indian Monuments Identifier",
    page_icon="🏛️",
    layout="centered",
)

# ── Monument metadata (cached JSON) ──────────────────────────
# Run once: python build_metadata.py  →  monument_metadata.json
# Or use the inline dict below as fallback.

MONUMENT_META = {
    "Taj Mahal": {
        "history": "Built between 1631–1648 by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. A UNESCO World Heritage Site and one of the Seven Wonders of the World.",
        "hours": "Sunrise to Sunset (closed on Fridays)",
        "ticket": "₹50 (Indian) | ₹1,100 (Foreign) | Free under 15 yrs",
        "location": "Agra, Uttar Pradesh",
        "lat": 27.1751, "lng": 78.0421,
    },
    "Red Fort": {
        "history": "Commissioned by Mughal Emperor Shah Jahan in 1638, it served as the main residence of the Mughal Emperors for nearly 200 years.",
        "hours": "9:30 AM – 4:30 PM (closed Mondays)",
        "ticket": "₹35 (Indian) | ₹500 (Foreign)",
        "location": "Delhi",
        "lat": 28.6562, "lng": 77.2410,
    },
    "Qutub Minar": {
        "history": "A 73-metre tall minaret built in 1193 by Qutub ud-Din Aibak. It is the world's tallest brick minaret and a UNESCO World Heritage Site.",
        "hours": "Sunrise to Sunset (all days)",
        "ticket": "₹35 (Indian) | ₹550 (Foreign)",
        "location": "New Delhi",
        "lat": 28.5244, "lng": 77.1855,
    },
    "Humayun's Tomb": {
        "history": "Built in 1570, it was the first garden-tomb on the Indian subcontinent and inspired several later monuments including the Taj Mahal.",
        "hours": "Sunrise to Sunset",
        "ticket": "₹35 (Indian) | ₹550 (Foreign)",
        "location": "New Delhi",
        "lat": 28.5933, "lng": 77.2507,
    },
    "Hawa Mahal": {
        "history": "Built in 1799 by Maharaja Sawai Pratap Singh of Jaipur. The 'Palace of Winds' has 953 windows designed to allow royal women to observe street life.",
        "hours": "9:00 AM – 5:00 PM",
        "ticket": "₹50 (Indian) | ₹200 (Foreign)",
        "location": "Jaipur, Rajasthan",
        "lat": 26.9239, "lng": 75.8267,
    },
    "India Gate": {
        "history": "A war memorial built in 1931 dedicated to 82,000 soldiers of the British Indian Army who died in World War I and the Third Anglo-Afghan War.",
        "hours": "Open 24 hours",
        "ticket": "Free",
        "location": "New Delhi",
        "lat": 28.6129, "lng": 77.2295,
    },
    "Mysore Palace": {
        "history": "The official residence of the Wadiyar dynasty, it was rebuilt between 1897 and 1912. It is one of India's most visited monuments.",
        "hours": "10:00 AM – 5:30 PM",
        "ticket": "₹70 (Indian) | ₹200 (Foreign)",
        "location": "Mysuru, Karnataka",
        "lat": 12.3052, "lng": 76.6552,
    },
    "Konark Sun Temple": {
        "history": "A 13th-century Sun temple at Konark in Odisha. Designed as a giant chariot with 12 pairs of stone wheels, it is a UNESCO World Heritage Site.",
        "hours": "6:00 AM – 8:00 PM",
        "ticket": "₹40 (Indian) | ₹600 (Foreign)",
        "location": "Konark, Odisha",
        "lat": 19.8876, "lng": 86.0945,
    },
    "Meenakshi Temple": {
        "history": "A historic Hindu temple dedicated to Parvati (Meenakshi) and Shiva (Sundareswarar). The temple has been rebuilt in the 17th century on an ancient site.",
        "hours": "5:00 AM – 12:30 PM & 4:00 PM – 9:30 PM",
        "ticket": "Free (camera fee: ₹50)",
        "location": "Madurai, Tamil Nadu",
        "lat": 9.9195, "lng": 78.1193,
    },
    "Charminar": {
        "history": "Built in 1591 by Muhammad Quli Qutb Shah to commemorate the founding of Hyderabad. Its name means 'Four Minarets' in Urdu.",
        "hours": "9:30 AM – 5:30 PM (closed Fridays)",
        "ticket": "₹25 (Indian) | ₹300 (Foreign)",
        "location": "Hyderabad, Telangana",
        "lat": 17.3616, "lng": 78.4747,
    },
    "Amber Fort": {
        "history": "A fort-palace complex atop a hill in Amer, Rajasthan, built from 1592 onward by Raja Man Singh I. Known for its artistic Hindu-Mughal architecture.",
        "hours": "8:00 AM – 5:30 PM (night tour: 7 PM – 10 PM)",
        "ticket": "₹100 (Indian) | ₹500 (Foreign)",
        "location": "Amer, Rajasthan",
        "lat": 26.9855, "lng": 75.8513,
    },
    "Victoria Memorial": {
        "history": "Built between 1906 and 1921 in memory of Queen Victoria, it is a marble museum and tourist destination in Kolkata.",
        "hours": "10:00 AM – 5:00 PM (closed Mondays)",
        "ticket": "₹30 (Indian) | ₹500 (Foreign)",
        "location": "Kolkata, West Bengal",
        "lat": 22.5448, "lng": 88.3426,
    },
    "Gateway of India": {
        "history": "An arch-monument built in Mumbai to commemorate the landing of King George V and Queen Mary in 1911. Completed in 1924.",
        "hours": "Open 24 hours",
        "ticket": "Free",
        "location": "Mumbai, Maharashtra",
        "lat": 18.9220, "lng": 72.8347,
    },
    "Ajanta Caves": {
        "history": "A series of 30 rock-cut Buddhist cave monuments in Maharashtra dating back to the 2nd century BCE. A UNESCO World Heritage Site famous for murals and sculptures.",
        "hours": "9:00 AM – 5:30 PM (closed Mondays)",
        "ticket": "₹40 (Indian) | ₹600 (Foreign)",
        "location": "Aurangabad, Maharashtra",
        "lat": 20.5519, "lng": 75.7033,
    },
    "Ellora Caves": {
        "history": "A UNESCO World Heritage Site featuring 100 cave temples and monasteries cut from basaltic rock between the 6th and 11th centuries CE, showcasing Hindu, Buddhist, and Jain art.",
        "hours": "6:00 AM – 6:00 PM (closed Tuesdays)",
        "ticket": "₹40 (Indian) | ₹600 (Foreign)",
        "location": "Aurangabad, Maharashtra",
        "lat": 20.0268, "lng": 75.1788,
    },
    "Sanchi Stupa": {
        "history": "The oldest stone structure in India, the Great Stupa at Sanchi was originally commissioned by Emperor Ashoka in the 3rd century BCE.",
        "hours": "Sunrise to Sunset",
        "ticket": "₹30 (Indian) | ₹500 (Foreign)",
        "location": "Sanchi, Madhya Pradesh",
        "lat": 23.4798, "lng": 77.7395,
    },
    "Fatehpur Sikri": {
        "history": "A city founded in 1571 by the Mughal Emperor Akbar and served as his capital for 14 years. A UNESCO World Heritage Site.",
        "hours": "Sunrise to Sunset",
        "ticket": "₹50 (Indian) | ₹610 (Foreign)",
        "location": "Agra, Uttar Pradesh",
        "lat": 27.0945, "lng": 77.6632,
    },
    "Mahabalipuram": {
        "history": "A group of 7th and 8th century CE monuments and temples built by Pallava kings. A UNESCO World Heritage Site known for its Shore Temple.",
        "hours": "6:00 AM – 6:00 PM",
        "ticket": "₹40 (Indian) | ₹600 (Foreign)",
        "location": "Chengalpattu, Tamil Nadu",
        "lat": 12.6269, "lng": 80.1927,
    },
}

# Try loading from JSON file (generated by scraper)
META_FILE = "monument_metadata.json"
if os.path.exists(META_FILE):
    with open(META_FILE) as f:
        MONUMENT_META.update(json.load(f))

# ── Load model ────────────────────────────────────────────────
MODEL_FILE   = "monument_classifier.pth"
CLASSES_FILE = "classes.json"

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(CLASSES_FILE):
        return None, None

    with open(CLASSES_FILE) as f:
        class_names = json.load(f)

    device = torch.device("cpu")

    # Rebuild same architecture used in training
    m = models.efficientnet_b2(weights=None)
    in_features = m.classifier[1].in_features
    m.classifier = nn.Sequential(
        nn.Dropout(p=0.4),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, len(class_names)),
    )
    ckpt = torch.load(MODEL_FILE, map_location=device)
    m.load_state_dict(ckpt["model_state_dict"])
    m.eval()
    return m, class_names

model, class_names = load_model()

# ── Inference helpers ─────────────────────────────────────────
INF_TF = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

def predict(img: Image.Image):
    tensor = INF_TF(img.convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1)[0]
    top5_probs, top5_idx = probs.topk(5)
    top5 = [(class_names[i], float(p)) for i, p in zip(top5_idx, top5_probs)]
    return top5

def google_maps_url(name, lat=None, lng=None):
    if lat and lng:
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    q = urllib.parse.quote(f"{name} monument India")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

# ── CLIP zero-shot fallback ───────────────────────────────────
@st.cache_resource
def load_clip():
    try:
        from transformers import CLIPProcessor, CLIPModel
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        return clip_model, clip_proc
    except Exception:
        return None, None

CLIP_LABELS = [
    "Taj Mahal", "Red Fort", "Qutub Minar", "Humayun's Tomb",
    "Hawa Mahal", "India Gate", "Mysore Palace", "Konark Sun Temple",
    "Meenakshi Temple", "Charminar", "Amber Fort", "Victoria Memorial",
    "Gateway of India", "Ajanta Caves", "Ellora Caves",
    "Sanchi Stupa", "Fatehpur Sikri", "Mahabalipuram",
]

def predict_clip(img: Image.Image):
    clip_model, clip_proc = load_clip()
    if clip_model is None:
        return None
    texts = [f"a photo of {n}" for n in CLIP_LABELS]
    inputs = clip_proc(text=texts, images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        out    = clip_model(**inputs)
        probs  = out.logits_per_image.softmax(dim=1)[0]
    top5_probs, top5_idx = probs.topk(5)
    return [(CLIP_LABELS[i], float(p)) for i, p in zip(top5_idx, top5_probs)]

# ── UI ────────────────────────────────────────────────────────
st.title("Indian Monuments & Heritage Identifier")
st.caption("Upload a photo of an Indian monument to get its name, history, visiting hours, ticket prices, and location.")

# Sidebar: mode info
with st.sidebar:
    st.header("About")
    if model:
        st.success("Fine-tuned EfficientNet-B2 loaded")
    else:
        st.warning("Model file not found – using CLIP zero-shot fallback.")
    st.markdown("**Dataset:** 24 Indian monuments (~3.5k images)")
    st.markdown("**Task:** T12.1 – Monuments & Heritage Identifier")
    st.markdown("---")
    st.markdown("Built with PyTorch + Streamlit")

uploaded = st.file_uploader("Upload a monument photo", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Identifying monument…"):
        if model:
            top5 = predict(img)
        else:
            top5 = predict_clip(img)

    if not top5:
        st.error("Could not run inference. Please ensure model or CLIP is available.")
        st.stop()

    name, confidence = top5[0]

    # ── Confidence threshold ──────────────────────────────────
    # If the top prediction is below this, the monument is likely
    # not in the training set.
    CONFIDENCE_THRESHOLD = 0.40

    st.divider()

    if confidence < CONFIDENCE_THRESHOLD:
        st.warning(
            f"**Monument not recognised.**\n\n"
            f"The model's best guess was **{name}** but with only "
            f"**{confidence*100:.1f}%** confidence — too low to be reliable.\n\n"
            f"This monument is likely **not in the training dataset** "
            f"(which covers 24 Indian monuments). Try a clearer photo, "
            f"or check if the monument is in the supported list below."
        )
        with st.expander("Show top-5 guesses anyway"):
            import pandas as pd
            df = pd.DataFrame(top5, columns=["Monument", "Probability"])
            df["Probability (%)"] = (df["Probability"] * 100).round(2)
            st.bar_chart(df.set_index("Monument")["Probability (%)"])
        st.stop()

    # ── Result card ──────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"{name}")
        st.metric("Confidence", f"{confidence*100:.1f}%")
    with col2:
        meta = MONUMENT_META.get(name, {})
        if meta.get("lat"):
            maps_url = google_maps_url(name, meta["lat"], meta["lng"])
        else:
            maps_url = google_maps_url(name)
        st.link_button("Open in Google Maps", maps_url, use_container_width=True)

    # ── Metadata ─────────────────────────────────────────────
    if meta:
        st.markdown("### History")
        st.info(meta.get("history", "No history available."))

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Location",  meta.get("location", "—"))
        col_b.metric("Hours",     meta.get("hours",    "—"))
        col_c.metric("Ticket",   meta.get("ticket",   "—"))
    else:
        st.warning(f"Metadata for **{name}** not found in the local database. "
                   "Consider running the Wikipedia scraper to enrich it.")

    # ── Top-5 bar chart ──────────────────────────────────────
    with st.expander("Show top-5 predictions"):
        import pandas as pd
        df = pd.DataFrame(top5, columns=["Monument", "Probability"])
        df["Probability (%)"] = (df["Probability"] * 100).round(2)
        st.bar_chart(df.set_index("Monument")["Probability (%)"])

    # ── Feedback ─────────────────────────────────────────────
    st.divider()
    st.markdown("**Was this correct?**")
    cols = st.columns(3)
    if cols[0].button("Yes"):
        st.success("Thank you for the feedback!")
    if cols[1].button("No"):
        correct = st.text_input("What is the correct monument?")
        if correct:
            st.info(f"Logged: '{correct}'. Thank you!")
    if cols[2].button("Not sure"):
        st.info("No problem!")

else:
    st.markdown("""
    ### How it works
    1. **Upload** a photo of any Indian monument.
    2. The model **identifies** the monument using a fine-tuned EfficientNet-B2.
    3. You get **history**, **visiting hours**, **ticket prices** and a **Google Maps** link.

    > **Supported monuments (24):** Taj Mahal, Red Fort, Qutub Minar, Hawa Mahal,
    > India Gate, Mysore Palace, Konark Sun Temple, Meenakshi Temple, Charminar,
    > Amber Fort, Victoria Memorial, Gateway of India, Ajanta Caves, Ellora Caves,
    > Sanchi Stupa, Fatehpur Sikri, Mahabalipuram, Humayun's Tomb, and more.
    """)