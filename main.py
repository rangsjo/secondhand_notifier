print("=== Container started ===")
print("Loading model...")

import time
import os
import requests
from sources.blocket import fetch_blocket
from sentence_transformers import SentenceTransformer
import numpy as np

HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
WEBHOOK_ID = os.getenv("WEBHOOK_ID", "begagnat_match")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 900))  # seconds

MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Example products
PRODUCTS = [
    {"name": "verktyg", "description": "hög kvalitet", "min_price": 0, "max_price": 5000}
]

# Precompute embeddings
for p in PRODUCTS:
    p["embedding"] = MODEL.encode(p["name"] + " " + p["description"])

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def send_webhook(product_name, listing, score):
    url = f"{HA_URL}/api/webhook/{WEBHOOK_ID}"
    payload = {
        "product": product_name,
        "title": listing["title"],
        "price": listing["price"],
        "url": listing["url"],
        "score": round(score,3)
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Webhook error:", e)

def scan():
    print("Starting scan...")
    for product in PRODUCTS:
        print(f"Searching for: {product['name']}")
        listings = fetch_blocket(product["name"])
        print(f"Found {len(listings)} listings")

        for listing in listings:
            text = listing["title"] + " " + listing["description"]
            emb = MODEL.encode(text)
            score = cosine_similarity(emb, product["embedding"])

            print(f"Checked: {listing['title']} | Score: {round(score,3)}")

            if score >= 0.7:
                print("MATCH FOUND!")
                send_webhook(product["name"], listing, score)

if __name__ == "__main__":
    while True:
        scan()
        print("Sleeping...")
        time.sleep(SCAN_INTERVAL)