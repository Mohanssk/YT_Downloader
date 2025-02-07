from fastapi import FastAPI, Response, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import yt_dlp
import os
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the download directory exists
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Serve the downloads directory as static files
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

class DownloadRequest(BaseModel):
    url: HttpUrl  # Ensures valid URL format

def download_video_task(url: str):
    """Background task to download the video."""
    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=True)
            filename = ydl.prepare_filename(info)
            return os.path.basename(filename) if filename else None

    except Exception as e:
        print(f"Download error: {e}")
        return None

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Handle video download request."""
    if not request.url:
        raise HTTPException(status_code=400, detail="No URL provided")
    
    filename = download_video_task(str(request.url))
    
    if filename:
        file_url = f"/downloads/{filename}"
        return {"message": "Download complete!", "file_url": file_url}
    else:
        raise HTTPException(status_code=500, detail="Download failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
