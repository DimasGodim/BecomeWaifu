import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("u9J87-E5l-03809")
    url_database:  str = Field("mysql://root:230205@localhost:3306/data")

config = Config()
