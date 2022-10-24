import logging

from fastapi import (
    FastAPI,
    UploadFile,
    FastAPI,
    Response,
    Request,
    Depends,
    HTTPException,
)
from uuid import uuid4, UUID

from json import load, JSONDecodeError

from models import FileData, SessionData
from session import backend, verifier, cookie, check_session_exists
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
async def create_session(file: UploadFile,
                         response: Response,
                         request: Request, session_id: UUID = Depends(check_session_exists)):
    """
    Асинхронный метод подсчёта суммы чисел в массиве из файла. Создаёт сессию и сохраняет данные:
    имя файла и сумму чисел
    """

    try:
        file_data = FileData(
            filename=file.filename,
            file_sum=sum(int(_) for _ in load(file.file)["array"] if _ is not None)
        )

        if not session_id:
            session_id = uuid4()
            log.info(f"New session: {session_id}")
            session_data = SessionData(files=[file_data])

            await backend.create(session_id, session_data)
            cookie.attach_to_response(response, session_id)
            log.debug(f"Session cookie: {response.headers.raw[0][1].decode()}")
        else:
            session_data = await backend.read(session_id)
            if session_data:
                session_data.files.append(file_data)
                await backend.update(session_id, session_data)
            else:
                session_data = SessionData(files=[file_data])
                await backend.create(session_id, session_data)

        await session_logger.log_session(str(session_id), file_data)

        return {
            "session_id": session_id,
            "file_data": file_data
        }
    except (JSONDecodeError, KeyError) as ex:
        log.error("Неверный вормат файла: не JSON формат", "JSON Decode error", exc_info=ex)
        raise HTTPException(status_code=415, detail="Unsupported Media Type")


@app.get("/sum", dependencies=[Depends(cookie)], response_model=SessionData)
async def get_sum(session_data: SessionData = Depends(verifier)):
    """
    Возвращает сохранённые данные: имя файла и сумму чисел в массиве файла
    """

    return session_data


@app.get("/sum-by-session-id", response_model=SessionData | str)
async def get_sum(session_id: str):
    """
    Возвращает сохранённые данные: имя файла и сумму чисел в массиве файла
    """

    session_data = await backend.read(UUID(session_id))

    if isinstance(session_data, SessionData):
        return session_data
    else:
        return "К сожалению по этому ID сессии ничего не найдено"
