from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from s3_utils import upload_file, download_file, list_versions
from auth import create_token, verify_token
from database import init_db, create_user, get_user, save_file_record, get_file_versions, get_all_files
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Register
@app.post("/register")
def register(username: str, password: str):
    hashed = pwd_context.hash(password)
    if create_user(username, hashed):
        return {"message": "User created successfully"}
    raise HTTPException(status_code=400, detail="Username already exists")

# Login
@app.post("/login")
def login(username: str, password: str):
    user = get_user(username)
    if not user or not pwd_context.verify(password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(username)
    return {"access_token": token, "token_type": "bearer"}

# Upload
@app.post("/upload")
def upload(file: UploadFile = File(...), user: str = Depends(verify_token)):
    result = upload_file(file, user)
    save_file_record(user, file.filename, result["key"], result["version"], result["backup"])
    return {"message": "File uploaded", **result}

# Download
@app.get("/download/{key:path}")
def download(key: str, user: str = Depends(verify_token)):
    content = download_file(key)
    return {"content": content.decode('utf-8', errors='ignore')}

# Get versions
@app.get("/versions/{filename}")
def versions(filename: str, user: str = Depends(verify_token)):
    return get_file_versions(user, filename)

# Get all files
@app.get("/files")
def all_files(user: str = Depends(verify_token)):
    return get_all_files(user)