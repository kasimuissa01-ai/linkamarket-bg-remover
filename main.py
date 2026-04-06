from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rembg import remove, new_session
import base64
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkaMarket BG Remover", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model ONCE at startup — not per request
# u2netp downloads automatically on first boot (~4.7MB)
logger.info("Loading u2netp model...")
SESSION = new_session("u2netp")
logger.info("✅ Model ready")


# ── POST /remove-bg-base64 ──────────────────────────────────────────
# Called by your Node.js imageGen.js
# Accepts: { "image_base64": "data:image/jpeg;base64,..." or raw base64 }
# Returns: { "success": true, "image_base64": "...", "processing_time_ms": 1240 }

class Base64Request(BaseModel):
    image_base64: str

@app.post("/remove-bg-base64")
async def remove_bg_base64(body: Base64Request):
    start = time.time()
    try:
        # Strip data URL prefix if present
        b64 = body.image_base64
        if "," in b64:
            b64 = b64.split(",", 1)[1]

        image_data = base64.b64decode(b64)

        if len(image_data) > 15 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image too large (max 15MB)")

        logger.info(f"Processing image: {len(image_data)} bytes")

        # Remove background — returns transparent PNG bytes
        result_bytes = remove(image_data, session=SESSION)
        result_b64   = base64.b64encode(result_bytes).decode("utf-8")

        elapsed = round((time.time() - start) * 1000)
        logger.info(f"✅ Done in {elapsed}ms")

        return JSONResponse({
            "success":            True,
            "image_base64":       result_b64,
            "processing_time_ms": elapsed,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /remove-bg ─────────────────────────────────────────────────
# Same thing but accepts a direct file upload

@app.post("/remove-bg")
async def remove_bg_file(file: UploadFile = File(...)):
    start = time.time()
    try:
        image_data = await file.read()

        if len(image_data) > 15 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image too large (max 15MB)")

        logger.info(f"Processing file: {file.filename}, {len(image_data)} bytes")

        result_bytes = remove(image_data, session=SESSION)
        result_b64   = base64.b64encode(result_bytes).decode("utf-8")

        elapsed = round((time.time() - start) * 1000)
        logger.info(f"✅ Done in {elapsed}ms")

        return JSONResponse({
            "success":            True,
            "image_base64":       result_b64,
            "processing_time_ms": elapsed,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Health check ────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "LinkaMarket BG Remover",
        "model":   "u2netp (4.7MB)",
        "status":  "running",
    }

@app.get("/health")
def health():
    return {"status": "ok", "model": "u2netp", "ready": SESSION is not None}