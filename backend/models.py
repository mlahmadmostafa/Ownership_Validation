from pydantic import BaseModel

class ServerRequest(BaseModel):
    file_path: str
    user_name: str
    model_name: str
    api_key: str
