from fastapi import FastAPI, UploadFile, FastAPI, Response, Depends
from uuid import UUID, uuid4

from json import load

from session import SessionData, backend, verifier, cookie


app = FastAPI()


@app.post("/uploadfile")
def create_upload_file(file: UploadFile):
    """
    Синхронный метод подсчёта суммы чисел в массиве из файла
    """

    return {"sum": sum(int(_) for _ in load(file.file)["array"] if _ is not None)}


@app.post("/uploadfile-async")
async def create_session(file: UploadFile, response: Response):
    """
    Асинхронный метод подсчёта суммы чисел в массиве из файла. Создаёт сессию и сохраняет данные:
    имя файла и сумму чисел
    """

    session = uuid4()
    data = SessionData(filename=file.filename, file_sum=sum(int(_) for _ in load(file.file)["array"] if _ is not None))

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {file.filename}"


@app.get("/sum", dependencies=[Depends(cookie)])
async def get_sum(session_data: SessionData = Depends(verifier)):
    """
    Возвращает сохранённые данные: имя файла и сумму чисел в массиве файла
    """

    return session_data