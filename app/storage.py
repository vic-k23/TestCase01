import logging
from uuid import UUID
from asyncio import run as async_run
from json import dumps, loads

from fastapi_sessions.frontends.session_frontend import ID
from fastapi_sessions.backends.implementations import InMemoryBackend

from aioredis import from_url
from aioredis.exceptions import DataError, ConnectionError

from models import SessionData
import settings

# logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class InMemoryStorage(InMemoryBackend[UUID, SessionData]):
    """
    Add read_all function
    """

    def __init__(self):
        super().__init__()

    async def read_all(self):
        """
        Return all records in storage
        """

        return self.data


class RedisStorage:
    """
    Uses Redis for storing data
    """

    def __init__(self):
        try:
            self.r = from_url(f"redis://{settings.REDIS_PARAMS.get('host', 'db')}"
                              f":{settings.REDIS_PARAMS.get('port', 6379)}",
                              # username=settings.REDIS_PARAMS.get('user', 'user'),
                              password=settings.REDIS_PARAMS.get('password', ''),
                              decode_responses=True
                              )

            if self.r:
                log.debug("Redis connected successfully")

        except Exception as ex:
            log.error("Error while connecting to Redis", exc_info=ex)

    def __del__(self):
        """
        Deleting self
        """
        if self.r:
            async_run(self.r.close())
            self.r.__del__()

    async def __aenter__(self):
        """
        Методы поддержки контекстного менеджера
        """

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Методы поддержки контекстного менеджера
        """

        if self.r:
            await self.r.close()
        return True

    async def redis_connected(self) -> bool:
        """
        Проверка подключения к Redis
        :return: True если подключение к серверу доступно.
        :rtype: bool
        """

        try:
            result = await self.r.ping()
            if result:
                return True
            return False
        except ConnectionError as conn_err:
            log.error("Connection error.", exc_info=conn_err)
            return False
        except Exception as ex:
            log.error("Нет подключения к Redis.\n", exc_info=ex)
            return False

    async def create(self, session_id: ID, data: SessionData):
        """Create a new session entry."""
        try:
            if not await self.r.set(str(session_id), dumps({"files": [item.__dict__ for item in data.files]})):
                log.error(f"Не удалось сохранить данные по {session_id=}: {data=}")
        except DataError as ex:
            log.error("Ошибка при попытке сохранить данные сессии: отсутствует ключ", exc_info=ex)
        except Exception as ex:
            log.error("Неизвестная ошибка при попытке сохранить данные сессии", exc_info=ex)

    async def read(self, session_id: ID) -> SessionData | None:
        """Read an existing session data."""
        try:
            data = await self.r.get(str(session_id))
            if not data:
                return

            return SessionData(**loads(data))
        except Exception as ex:
            log.error("Непредвиденная ошибка при чтении данных", exc_info=ex)

    async def update(self, session_id: ID, data: SessionData) -> None:
        """Update an existing session."""
        try:
            if not await self.r.set(str(session_id), dumps({"files": [item.__dict__ for item in data.files]}), xx=True):
                log.error(f"Похоже сессии с {session_id=} нет и не было")
        except DataError as ex:
            log.error("Ошибка при попытке обновить данные сессии: отсутствует ключ", exc_info=ex)
        except Exception as ex:
            log.error("Неизвестная ошибка при попытке обновить данные сессии", exc_info=ex)
            # raise BackendError("session does not exist, cannot update")

    async def delete(self, session_id: ID) -> None:
        """D"""
        try:
            await self.r.delete(str(session_id))
        except Exception as ex:
            log.error(f"Непредвиденная ошибка при удалении записи с {session_id=}", exc_info=ex)

    async def read_all(self):
        """
        Return all records in storage
        """

        try:
            keys = await self.r.keys()
            values = await self.r.mget(keys)
            alltogether = dict(map(lambda k, v: (UUID(k), loads(v)), keys, values))
            log.debug(f"{alltogether=}")
            return alltogether
        except Exception as ex:
            log.error("Непредвиденная ошибка при получении данных всех сессий из БД", exc_info=ex)
