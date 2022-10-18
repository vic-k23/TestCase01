from datetime import datetime
from json import load, dump
from pathlib import Path
from models import FileData


class SessionLogger:
    """
    Сохраняет историю сессий
    """

    def __init__(self, file_name: str = "sessions.json") -> None:
        """
        Инициализируем SessionLogger.
        :param file_name: Необязательный параметр для задания имени файла лога. По умолчанию равен sessions.log
        """

        self.sessions_log_file_name = file_name
        self.fp = Path(self.sessions_log_file_name)
        self.sessions_log = []

    async def open(self) -> None:
        """
        Открывает файл лога и считывает данные из него, если он существует
        """

        if self.fp.exists():
            with self.fp.open() as f:
                self.sessions_log = load(f)

    async def log_session(self, session_id: str, file_data: FileData) -> None:
        """
        Adds session data to log
        :param session_id: идентификатор сессии
        :param file_data: данные сессии в формате SessionData
        """

        self.sessions_log.append(
            {
                "time": datetime.now().isoformat(),
                "session_id": session_id,
                "session_filename": file_data.filename,
                "session_file_sum": file_data.file_sum
            }
        )

    async def save_log(self):
        """
        Saves log into the file. Only last 100 sessions.
        """

        if len(self.sessions_log) > 100:
            self.sessions_log = self.sessions_log[-100:]

        with self.fp.open(mode="w") as f:
            dump(self.sessions_log, f, indent=1)
