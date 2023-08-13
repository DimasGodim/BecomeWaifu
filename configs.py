import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("")
    url_database:  str = Field("")
    redirect_uri_register: str = Field("")
    redirect_uri_login: str = Field("")
    redirect_uri_page_masuk: str = Field("")
    password_email: str = Field("")
    email: str = Field("")

config = Config()
