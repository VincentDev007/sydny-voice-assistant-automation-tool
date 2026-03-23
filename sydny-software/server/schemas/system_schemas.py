from pydantic import BaseModel

class VolumeRequest(BaseModel):
    level: int                    # Volume level (0-100)

class AppRequest(BaseModel):
    app_name: str                 # Application name (e.g., "Safari", "Spotify")

class FileRequest(BaseModel):
    filepath: str                 # Full path to a file

class MoveFileRequest(BaseModel):
    source: str                   # Source file path
    destination: str              # Destination file path

class SearchRequest(BaseModel):
    filename: str                 # Filename to search for