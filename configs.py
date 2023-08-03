import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("")
    url_database:  str = Field("mysql://root:230205@localhost:3306/data")
    redirect_uri: str = Field("https://ea49-125-163-155-235.ngrok-free.app/auth2callback")
    redirect_uri_complete: str = Field("https://ea49-125-163-155-235.ngrok-free.app")

config = Config()
