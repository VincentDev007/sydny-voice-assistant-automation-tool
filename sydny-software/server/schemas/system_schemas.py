from pydantic import BaseModel

class VolumeRequest(BaseModel):
    level: int

class AppRequest(BaseModel):
    app_name: str

class FileRequest(BaseModel):
    filepath: str

class MoveFileRequest(BaseModel):
    source: str
    destination: str

class SearchRequest(BaseModel):
    filename: str
