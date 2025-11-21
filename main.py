import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Artisan, Registration

app = FastAPI(title="Handcrafted Arts Initiative API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApiMessage(BaseModel):
    message: str


@app.get("/", response_model=ApiMessage)
def read_root():
    return {"message": "Backend running"}


@app.get("/api/hello", response_model=ApiMessage)
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -----------------------------
# Artisans Endpoints
# -----------------------------

@app.post("/api/artisans", response_model=dict)
def create_artisan(artisan: Artisan):
    try:
        inserted_id = create_document("artisan", artisan)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/artisans", response_model=List[dict])
def list_artisans(category: Optional[str] = None, region: Optional[str] = None, featured: Optional[bool] = None, limit: int = 24):
    filt: dict = {}
    if category:
        filt["craft_type"] = category
    if region:
        filt["region"] = region
    if featured is not None:
        filt["featured"] = featured
    try:
        docs = get_documents("artisan", filt, limit)
        # Convert ObjectId to string
        from bson import ObjectId
        for d in docs:
            if isinstance(d.get("_id"), ObjectId):
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception:
        # If bson not available, still return raw docs
        return docs


# -----------------------------
# Registration Endpoint (Google Sheets webhook optional)
# -----------------------------

@app.post("/api/register", response_model=dict)
def register_artisan(payload: Registration):
    # Save to DB
    try:
        reg_id = create_document("registration", payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    # Forward to Google Sheets Apps Script if configured
    webhook = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL")
    forwarded = False
    forward_status = None
    if webhook:
        try:
            import requests
            data = payload.model_dump()
            data.update({
                "_source": "website",
                "_received_at": datetime.now(timezone.utc).isoformat(),
                "_registration_id": reg_id,
            })
            r = requests.post(webhook, json=data, timeout=10)
            forwarded = r.ok
            forward_status = r.status_code
        except Exception as e:
            forward_status = f"error: {str(e)[:120]}"

    return {"ok": True, "id": reg_id, "forwarded": forwarded, "forward_status": forward_status}


# -----------------------------
# Simple analytics ping
# -----------------------------

class Event(BaseModel):
    name: str
    meta: Optional[dict] = None


@app.post("/api/event", response_model=dict)
def track_event(ev: Event):
    try:
        create_document("event", {"name": ev.name, "meta": ev.meta or {}, "ts": datetime.now(timezone.utc)})
    except Exception:
        pass
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
