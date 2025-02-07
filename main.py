from fastapi import FastAPI, Response, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Define a request model
class DownloadRequest(BaseModel):
    url: str
    output_path: str = "downloads"

# Ensure the download directory exists
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def download_video_task(url: str, output_path: str):
    """Background task to download the video."""
    ydl_opts = {
        "format": "best",
        "outtmpl": f"{output_path}/%(title)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

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

    video_output_path = os.path.join(DOWNLOADS_DIR, request.output_path)
    os.makedirs(video_output_path, exist_ok=True)

    background_tasks.add_task(download_video_task, request.url, video_output_path)

    return {"message": "Download started!", "file_url": f"/static/{request.output_path}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
