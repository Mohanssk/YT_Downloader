import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import yt_dlp
from typing import Optional

app = FastAPI()

# Ensure the downloads directory exists
os.makedirs("downloads", exist_ok=True)

# Root endpoint to check server status
@app.get("/")
def read_root():
    return {"message": "Server is up and running!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mohanssk.github.io/YT_Downloader/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

class DownloadRequest(BaseModel):
    url: str
    output_path: Optional[str] = 'downloads'

@app.post("/download")
async def download_video(request: DownloadRequest):
    url = request.url
    output_path = request.output_path

    # Check if the cookies file exists
    if not os.path.exists('cookies.txt'):
        raise HTTPException(status_code=400, detail="Cookies file (cookies.txt) not found. Please provide a valid cookies file.")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
    }

    try:
        os.makedirs(output_path, exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = sorted(
            (f for f in os.listdir(output_path) if f.endswith('.mp4')),
            key=lambda f: os.path.getctime(os.path.join(output_path, f)),
            reverse=True
        )

        if downloaded_files:
            filename = downloaded_files[0]
            file_url = f"/downloads/{filename}"
            return {"message": "Download completed successfully.", "file_url": file_url}
        else:
            raise HTTPException(status_code=500, detail="Download completed, but no MP4 files were found.")

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"YouTube download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
