from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; change to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.options("/download")
async def options_download(response: Response):
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.post("/download")
def download_video():
    return {"message": "Downloading..."}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT env is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
