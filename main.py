import os
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store uploaded files and serve static files
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create test files for download speed test
DOWNLOAD_FILE_SIZES = [1, 10, 100]  # sizes in MB
for size in DOWNLOAD_FILE_SIZES:
    file_path = os.path.join(UPLOAD_DIR, f"test_file_{size}MB.bin")
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(os.urandom(size * 1024 * 1024))

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    end_time = time.time()
    file_size = os.path.getsize(file_path)
    upload_speed = file_size / (end_time - start_time) / (1024 * 1024)  # MB/s
    
    return JSONResponse({
        "filename": file.filename,
        "size": file_size,
        "speed": round(upload_speed, 2)
    })

@app.get("/download/{size}")
async def download_file(size: int):
    if size not in DOWNLOAD_FILE_SIZES:
        raise HTTPException(status_code=400, detail="Invalid file size")
    
    file_path = os.path.join(UPLOAD_DIR, f"test_file_{size}MB.bin")
    return FileResponse(file_path, filename=f"speed_test_{size}MB.bin")

@app.get("/speed")
async def get_speed(size: int, time_taken: float):
    if size not in DOWNLOAD_FILE_SIZES:
        raise HTTPException(status_code=400, detail="Invalid file size")
    
    file_size = size * 1024 * 1024  # Convert MB to bytes
    speed = file_size / time_taken / (1024 * 1024)  # MB/s
    return JSONResponse({"speed": round(speed, 2)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)