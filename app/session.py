import logging

from fastapi import Request, HTTPException
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

from itsdangerous import BadSignature, SignatureExpired
from uuid import UUID

from models import SessionData

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

cookie_params = CookieParameters()

cookie = SessionCookie(
    cookie_name="file_upload",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


def check_session_exists(request: Request) -> UUID | bool:
    """
    Проверяем, существует ли сессия
    """

    try:
        signed_session_id = request.cookies.get(cookie.model.name)
        if signed_session_id is None:
            return False
        return UUID(
            cookie.signer.loads(
                signed_session_id,
                max_age=cookie.cookie_params.max_age,
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
        backend: InMemoryBackend[UUID, SessionData],
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


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session")
)
