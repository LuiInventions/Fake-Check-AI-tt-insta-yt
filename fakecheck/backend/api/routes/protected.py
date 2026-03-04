from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from config import get_settings, Settings
import os

router = APIRouter()

class PasswordRequest(BaseModel):
    password: str

@router.post("/verify-password")
async def verify_password(req: PasswordRequest, settings: Settings = Depends(get_settings)):
    if req.password == settings.START_SITE_PASSWORD:
        return JSONResponse(content={"status": "success"}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.get("/protected-download/{filename}")
async def protected_download(filename: str, password: str, settings: Settings = Depends(get_settings)):
    import sys
    print("ROUTE ACCESSED", flush=True)
    if password != settings.START_SITE_PASSWORD:
        print("WRONG PASSWORD", flush=True)
        raise HTTPException(status_code=401, detail="Invalid password")
    
    print("PASSWORD CORRECT", flush=True)
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    protected_dir = "/app/data/protected_downloads"
    file_path = os.path.join(protected_dir, filename)
    print("FILE PATH:", file_path, flush=True)
    
    if not os.path.exists(file_path):
        print("FILE NOT EXIST", flush=True)
        raise HTTPException(status_code=404, detail="File not found")
        
    print("READING FILE", flush=True)
    from fastapi import Response
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    print("RETURNING RESPONSE", flush=True)
    return Response(content=file_data, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
