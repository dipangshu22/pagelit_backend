from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import os
import io

app = FastAPI()

# 🔥 CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pagelit-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================================================
# 1️⃣ IMAGE → TEXT (Disabled Safe Version)
# =========================================================
@app.post("/image-to-text")
async def image_to_text(file: UploadFile = File(...)):
    try:
        return {
            "extracted_text": "OCR is temporarily disabled in production. Enable via Docker setup."
        }
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
            contents = await file.read()
            img = Image.open(io.BytesIO(contents)).convert("RGB")
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
# 3️⃣ REMOVE BACKGROUND (Disabled Safe Version)
# =========================================================
@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    try:
        return JSONResponse({
            "message": "Background removal disabled in free production environment."
        })
    except Exception as e:
        return JSONResponse({"error": str(e)})


# =========================================================
# ROOT CHECK (Health Check)
# =========================================================
@app.get("/")
def root():
    return {"status": "Backend running successfully 🚀"}