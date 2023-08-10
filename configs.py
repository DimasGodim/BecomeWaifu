import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("L131S861G_e-B69")
    url_database:  str = Field("mysql://root:123456@localhost:3306/data")
    redirect_uri_register: str = Field("https://afb3-36-80-227-71.ngrok-free.app/auth2callbackRegister")
    redirect_uri_login: str = Field("https://afb3-36-80-227-71.ngrok-free.app/auth2callbackLogin")
    redirect_uri_page_masuk: str = Field("localhost:8000/")

config = Config()
