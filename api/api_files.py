from fastapi import APIRouter, HTTPException, UploadFile

files_router = APIRouter()

@files_router.post("/upload/")
async def create_upload_image_file(file: UploadFile):
    print(type(file))
    content_type = file.content_type
    file_size = file.size
    
    if content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=415, detail="File type not supported. Only jpeg, png and gif are supported")
    
    if file_size is None:
        raise HTTPException(status_code=400, detail="File size is not specified")
    
    if file_size > 1 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size is greater than 1 MB")
    
    return {"filename": file.filename, "content_type": content_type, "file_size": file_size}
