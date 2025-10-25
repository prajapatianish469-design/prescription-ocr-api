from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
import os
import subprocess

app = FastAPI()

# ✅ Allow your frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Install tesseract at runtime (important for Render)
TESSERACT_PATH = "/usr/bin/tesseract"
if not os.path.exists(TESSERACT_PATH):
    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "tesseract-ocr"], check=True)
    except Exception as e:
        print("⚠️ Failed to install Tesseract:", e)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


@app.get("/")
def home():
    return {"message": "Prescription OCR API is running!"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    known_medicines = [
        "paracetamol", "amoxicillin", "cetirizine",
        "ibuprofen", "azithromycin", "metformin", "dolo", "crocin"
    ]

    detected_medicines = []
    quantities = []

    text_lower = text.lower()

    for line in text_lower.split("\n"):
        for med in known_medicines:
            if med in line:
                detected_medicines.append({"name": med.capitalize()})
                qty_match = re.search(r'(\d+)\s*(tablet|tab|pcs|x)?', line)
                qty = int(qty_match.group(1)) if qty_match else 1
                quantities.append(qty)
                break

    return {
        "detected_medicines": detected_medicines,
        "quantities": quantities
    }

