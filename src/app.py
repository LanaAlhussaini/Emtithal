from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

from src.pipeline import run_pipeline
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/contracts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Imtithal backend running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_pipeline(file_path)
    result["uploaded_file"] = file.filename

    return result