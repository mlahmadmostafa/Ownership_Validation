from fastapi import FastAPI
from .models import ServerRequest
from src.ownership_validator import generate_quiz
app = FastAPI()

@app.post("/")
def read_root(request: ServerRequest):
    generate_quiz(request.file_path, request.model_name, request.api_key)
    return request
