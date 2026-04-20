# =============================================================
# build_metadata.py
# Scrapes Wikipedia for monument metadata and saves as JSON.
# Run once before deploying the Streamlit app.
# pip install wikipedia-api requests
# =============================================================

import json, time, requests
import wikipediaapi

MONUMENTS = [
    "Taj Mahal",
    "Red Fort",
    "Qutub Minar",
    "Humayun's Tomb",
    "Hawa Mahal",
    "India Gate",
    "Mysore Palace",
    "Konark Sun Temple",
    "Meenakshi Temple",
    "Charminar",
    "Amber Fort",
    "Victoria Memorial, Kolkata",
    "Gateway of India",
    "Ajanta Caves",
    "Ellora Caves",
    "Sanchi",
    "Fatehpur Sikri",
    "Mahabalipuram",
    "Khajuraho",
    "Nalanda",
    "Rani ki vav",
    "Brihadeeswarar Temple",
    "Golkonda fort",
    "Jaisalmer Fort",
]

# Hardcoded visit info (Wikipedia doesn't structure this well)
VISIT_INFO = {
    "Taj Mahal":           {"hours": "Sunrise–Sunset (Fri closed)", "ticket": "₹50 / ₹1100", "location": "Agra, UP", "lat": 27.1751, "lng": 78.0421},
    "Red Fort":            {"hours": "9:30–4:30 (Mon closed)",       "ticket": "₹35 / ₹500",  "location": "Delhi",    "lat": 28.6562, "lng": 77.2410},
    "Qutub Minar":         {"hours": "Sunrise–Sunset",               "ticket": "₹35 / ₹550",  "location": "New Delhi","lat": 28.5244, "lng": 77.1855},
    "Humayun's Tomb":      {"hours": "Sunrise–Sunset",               "ticket": "₹35 / ₹550",  "location": "New Delhi","lat": 28.5933, "lng": 77.2507},
    "Hawa Mahal":          {"hours": "9:00–5:00",                    "ticket": "₹50 / ₹200",  "location": "Jaipur, RJ","lat": 26.9239,"lng": 75.8267},
    "India Gate":          {"hours": "Open 24 hours",                "ticket": "Free",         "location": "New Delhi","lat": 28.6129, "lng": 77.2295},
    "Mysore Palace":       {"hours": "10:00–5:30",                   "ticket": "₹70 / ₹200",  "location": "Mysuru, KA","lat": 12.3052,"lng": 76.6552},
    "Konark Sun Temple":   {"hours": "6:00–8:00",                    "ticket": "₹40 / ₹600",  "location": "Konark, OD","lat": 19.8876,"lng": 86.0945},
    "Meenakshi Temple":    {"hours": "5:00–12:30 & 4:00–9:30",       "ticket": "Free",         "location": "Madurai, TN","lat": 9.9195,"lng": 78.1193},
    "Charminar":           {"hours": "9:30–5:30 (Fri closed)",       "ticket": "₹25 / ₹300",  "location": "Hyderabad, TG","lat": 17.3616,"lng": 78.4747},
    "Amber Fort":          {"hours": "8:00–5:30",                    "ticket": "₹100 / ₹500", "location": "Amer, RJ", "lat": 26.9855, "lng": 75.8513},
    "Victoria Memorial, Kolkata":{"hours":"10:00–5:00 (Mon closed)", "ticket": "₹30 / ₹500",  "location": "Kolkata, WB","lat": 22.5448,"lng": 88.3426},
    "Gateway of India":    {"hours": "Open 24 hours",                "ticket": "Free",         "location": "Mumbai, MH","lat": 18.9220,"lng": 72.8347},
    "Ajanta Caves":        {"hours": "9:00–5:30 (Mon closed)",       "ticket": "₹40 / ₹600",  "location": "Aurangabad, MH","lat": 20.5519,"lng": 75.7033},
    "Ellora Caves":        {"hours": "6:00–6:00 (Tue closed)",       "ticket": "₹40 / ₹600",  "location": "Aurangabad, MH","lat": 20.0268,"lng": 75.1788},
    "Sanchi":              {"hours": "Sunrise–Sunset",                "ticket": "₹30 / ₹500",  "location": "Sanchi, MP","lat": 23.4798,"lng": 77.7395},
    "Fatehpur Sikri":      {"hours": "Sunrise–Sunset",               "ticket": "₹50 / ₹610",  "location": "Agra, UP", "lat": 27.0945, "lng": 77.6632},
    "Mahabalipuram":       {"hours": "6:00–6:00",                    "ticket": "₹40 / ₹600",  "location": "Chengalpattu, TN","lat": 12.6269,"lng": 80.1927},
    "Khajuraho":           {"hours": "Sunrise–Sunset",               "ticket": "₹40 / ₹600",  "location": "Chhatarpur, MP","lat": 24.8502,"lng": 79.9218},
    "Nalanda":             {"hours": "9:00–5:00 (Fri closed)",       "ticket": "₹20 / ₹300",  "location": "Nalanda, BR","lat": 25.1357,"lng": 85.4437},
    "Rani ki vav":         {"hours": "8:00–6:00",                    "ticket": "₹35 / ₹550",  "location": "Patan, GJ","lat": 23.8588,"lng": 72.1013},
    "Brihadeeswarar Temple":{"hours":"6:00–12:30 & 4:00–8:30",      "ticket": "Free",         "location": "Thanjavur, TN","lat": 10.7825,"lng": 79.1318},
    "Golkonda fort":       {"hours": "8:00–5:00",                    "ticket": "₹25 / ₹200",  "location": "Hyderabad, TG","lat": 17.3833,"lng": 78.4011},
    "Jaisalmer Fort":      {"hours": "Open 24 hours (museum 9–5)",   "ticket": "₹50 / ₹250",  "location": "Jaisalmer, RJ","lat": 26.9124,"lng": 70.9101},
}


def get_wikipedia_summary(title: str) -> str:
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="MonumentIdentifierBot/1.0 (academic-project)"
    )
    page = wiki.page(title)
    if page.exists():
        # Return first 3 sentences
        text = page.summary
        sentences = text.split(". ")
        return ". ".join(sentences[:3]) + "."
    return ""


def build_metadata():
    metadata = {}
    for monument in MONUMENTS:
        print(f"Fetching: {monument}")
        try:
            history = get_wikipedia_summary(monument)
        except Exception as e:
            print(f"  Error: {e}")
            history = ""

        # Normalize key to match class names
        key = monument.replace(", Kolkata", "")  # strip city suffix for display

        info = VISIT_INFO.get(monument, {})
        metadata[key] = {
            "history": history or "Historical information unavailable.",
            "hours":    info.get("hours",    "Check official website"),
            "ticket":   info.get("ticket",   "Check official website"),
            "location": info.get("location", "India"),
            "lat":      info.get("lat",      None),
            "lng":      info.get("lng",      None),
        }
        time.sleep(1)   # be polite to Wikipedia

    with open("monument_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(metadata)} monuments to monument_metadata.json")


if __name__ == "__main__":
    build_metadata()