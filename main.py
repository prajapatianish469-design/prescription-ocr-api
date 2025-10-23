from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (your site will connect)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Prescription OCR API is running!"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)

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

    return {"detected_medicines": detected_medicines, "quantities": quantities}
