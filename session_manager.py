from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import UUID

cookie_params = CookieParameters()

backend = InMemoryBackend[UUID, dict]()
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="230205",  # Ganti dengan secret key yang sesuai
    cookie_params=cookie_params,
)