import logging

from fastapi import FastAPI, UploadFile, FastAPI, Response, Depends, HTTPException
from uuid import uuid4

from json import load, JSONDecodeError

from session import SessionData, backend, verifier, cookie
from sessions_history import SessionLogger

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

session_logger = SessionLogger()

app = FastAPI()


@app.on_event("startup")
async def init_sessions_logger() -> None:
    """
    Открываем логер перед стартом сервиса
    """

    await session_logger.open()


@app.on_event("shutdown")
async def save_sessions_log() -> None:
    """
    Save sessions log
    """

    await session_logger.save_log()

@app.post("/uploadfile")
def create_upload_file(file: UploadFile):
    """
    Синхронный метод подсчёта суммы чисел в массиве из файла
    """

    try:
        d_json = load(file.file)
        return {"sum": sum(int(_) for _ in d_json["array"] if _ is not None)}

    except (JSONDecodeError, KeyError) as ex:
        log.error("Неверный вормат файла: не JSON формат", exc_info=ex)
        raise HTTPException(status_code=415, detail="Unsupported Media Type")


@app.post("/uploadfile-async")
async def create_session(file: UploadFile, response: Response):
    """
    Асинхронный метод подсчёта суммы чисел в массиве из файла. Создаёт сессию и сохраняет данные:
    имя файла и сумму чисел
    """

    try:
        session = uuid4()
        data = SessionData(filename=file.filename, file_sum=sum(int(_) for _ in load(file.file)["array"] if _ is not None))

        await backend.create(session, data)
        cookie.attach_to_response(response, session)

        await session_logger.log_session(data)

        return f"created session for {file.filename}"
    except (JSONDecodeError, KeyError) as ex:
        log.error("Неверный вормат файла: не JSON формат", "JSON Decode error", exc_info=ex)
        raise HTTPException(status_code=415, detail="Unsupported Media Type")


@app.get("/sum", dependencies=[Depends(cookie)], response_model=SessionData)
async def get_sum(session_data: SessionData = Depends(verifier)):
    """
    Возвращает сохранённые данные: имя файла и сумму чисел в массиве файла
    """

    return session_data
