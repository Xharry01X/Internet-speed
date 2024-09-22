import os
import time
import random
from fastapi import FastAPI, HTTPException
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

# Directory for test file
TEST_DIR = "test_files"
os.makedirs(TEST_DIR, exist_ok=True)

# Test file path
TEST_FILE_PATH = os.path.join(TEST_DIR, "test_file_100MB.bin")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def create_test_file():
    """Create a 100MB test file with random data."""
    file_size = 100 * 1024 * 1024  # 100 MB
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(os.urandom(file_size))

@app.on_event("startup")
async def startup_event():
    """Create test file on startup if it doesn't exist."""
    if not os.path.exists(TEST_FILE_PATH):
        create_test_file()

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/download")
async def download_file():
    if not os.path.exists(TEST_FILE_PATH):
        raise HTTPException(status_code=404, detail="Test file not found")
    return FileResponse(TEST_FILE_PATH, filename="test_file_100MB.bin")

@app.get("/upload")
async def simulate_upload():
    """Simulate an upload by reading the test file."""
    start_time = time.time()
    
    with open(TEST_FILE_PATH, "rb") as f:
        f.read()  # Read the entire file
    
    end_time = time.time()
    file_size = os.path.getsize(TEST_FILE_PATH)
    upload_speed = file_size / (end_time - start_time) / (1024 * 1024)  # MB/s
    
    return JSONResponse({
        "size": file_size,
        "speed": round(upload_speed, 2)
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)