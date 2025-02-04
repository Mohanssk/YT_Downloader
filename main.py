from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mohanssk.github.io/YT_Downloader/"],  # Change this to your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
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

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Force MP4 format
        'merge_output_format': 'mp4',  # Ensure final output is MP4
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',  # Use cookies if needed
    }

    try:
        os.makedirs(output_path, exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Check for downloaded files
        downloaded_files = sorted(
            (f for f in os.listdir(output_path) if f.endswith('.mp4')),  # Filter MP4 files only
            key=lambda f: os.path.getctime(os.path.join(output_path, f)),
            reverse=True
        )

        if downloaded_files:
            filename = downloaded_files[0]  # Get the most recent file
            file_url = f"/downloads/{filename}"
            return {"message": "Download completed successfully.", "file_url": file_url}
        else:
            raise HTTPException(status_code=500, detail="Download completed, but no MP4 files were found.")

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"YouTube download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
