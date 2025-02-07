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
    """Background task to download the video with authentication."""
    try:
        # Check if cookies.txt exists
        cookies_path = "cookies.txt"
        if not os.path.exists(cookies_path):
            print("Warning: cookies.txt not found. Some videos may require authentication.")

        # yt-dlp options
        ydl_opts = {
            "format": "best",
            "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),  # Save directly in 'downloads'
            "cookiefile": cookies_path if os.path.exists(cookies_path) else None,  # Use cookies if available
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=True)  # Convert URL to string
            filename = ydl.prepare_filename(info)
            return os.path.basename(filename) if filename else None

    except Exception as e:
        print(f"Download error: {e}")
        return None

@app.options("/download")
async def options_download(response: Response):
    """Handle CORS preflight requests."""
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Handle video download request."""
    if not request.url:
        raise HTTPException(status_code=400, detail="No URL provided")

    background_tasks.add_task(download_video_task, str(request.url))  # Run in background
    return {"message": "Download started! Check /downloads later for the file."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
