import logging
from uuid import UUID

from fastapi import Request, HTTPException
from fastapi_sessions.session_verifier import SessionVerifier
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from models import SessionData
from storage import InMemoryStorage, RedisStorage
import settings

# logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def check_session_exists(request: Request) -> UUID | bool:
    """
    Проверяем, существует ли сессия
    """

    try:
        signed_session_id = request.cookies.get(settings.COOKIE_PARAMS.get('cookie_name', 'file_upload'))
        if signed_session_id is None:
            return False
        return UUID(
            URLSafeTimedSerializer(
                settings.COOKIE_PARAMS.get('secret_key', "DONOTUSE"),
                salt=settings.COOKIE_PARAMS.get('cookie_name', 'file_upload')
            ).loads(
                signed_session_id,
                max_age=settings.COOKIE_PARAMS.get('max_age', 3600),
                return_timestamp=False,
            )
        )

    except (AttributeError, SignatureExpired, BadSignature) as ex:
        log.error("Не удалось получить идентификатор сессии, похоже, сессии не существует", exc_info=ex)
        return False


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
            self,
            *,
            identifier: str,
            auto_error: bool,
            backend: InMemoryStorage | RedisStorage,
            auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True
