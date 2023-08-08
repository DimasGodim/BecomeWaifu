import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("I55906n808M254E")
    url_database:  str = Field("mysql://root:123456@localhost:3306/data")
    redirect_uri_register: str = Field("https://ad46-180-254-85-187.ngrok-free.app/auth2callbackRegister")
    redirect_uri_login: str = Field("https://ad46-180-254-85-187.ngrok-free.app/auth2callbackLogin")
    redirect_uri_page_masuk: str = Field("https://ad46-180-254-85-187.ngrok-free.app")

config = Config()
