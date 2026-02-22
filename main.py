from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import pytesseract
import os
import cv2
import numpy as np
from rembg import remove

# 🔹 Set Tesseract path (Windows only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================================================
# 1️⃣ IMAGE → TEXT (OCR)
# =========================================================
@app.post("/image-to-text")
async def image_to_text(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return JSONResponse({"error": "Invalid image file"})

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2
        )

        thresh = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        custom_config = r'''
            --oem 3
            --psm 6
            -c preserve_interword_spaces=1
        '''

        text = pytesseract.image_to_string(
            thresh,
            config=custom_config,
            lang="eng"
        )

        return {"extracted_text": text.strip()}

    except Exception as e:
        return JSONResponse({"error": str(e)})

# =========================================================
# 2️⃣ MULTIPLE IMAGES → SINGLE PDF
# =========================================================
@app.post("/convert-to-pdf")
async def convert_to_pdf(files: List[UploadFile] = File(...)):
    try:
        images = []

        for file in files:
            img = Image.open(file.file).convert("RGB")
            images.append(img)

        if not images:
            return JSONResponse({"error": "No images uploaded"})

        pdf_path = os.path.join(UPLOAD_FOLDER, "converted.pdf")

        images[0].save(
            pdf_path,
            save_all=True,
            append_images=images[1:]
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="converted.pdf"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)})

# =========================================================
# 3️⃣ REMOVE BACKGROUND (AI)
# =========================================================
@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    try:
        input_bytes = await file.read()

        # AI background removal
        output_bytes = remove(input_bytes)

        output_path = os.path.join(UPLOAD_FOLDER, "background_removed.png")

        with open(output_path, "wb") as f:
            f.write(output_bytes)

        return FileResponse(
            output_path,
            media_type="image/png",
            filename="background_removed.png"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)})