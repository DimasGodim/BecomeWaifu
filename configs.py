import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("")
    url_database:  str = Field("")
    redirect_uri: str = Field("")
    redirect_uri_complete: str = Field("")

config = Config()
