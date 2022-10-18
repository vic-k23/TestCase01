from pydantic import BaseModel
from typing import List


class FileData(BaseModel):
    """
    Данные по загруженному файлу
    """

    filename: str
    file_sum: int


class SessionData(BaseModel):
    """
    Данные о загруженных во время сессии файлах
    """

    files: List[FileData]
