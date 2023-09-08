import os
from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_voicevox: str = Field("L131S861G_e-B69")
    url_database:  str = Field("mysql://dimas:230205@localhost:3306/data")
    redirect_uri_register: str = Field("https://4322-103-105-55-142.ngrok-free.app/auth2callbackRegister")
    redirect_uri_login: str = Field("https://4322-103-105-55-142.ngrok-free.app/auth2callbackLogin")
    redirect_uri_page_masuk: str = Field("https://4322-103-105-55-142.ngrok-free.app/page-masuk")
    password_email: str = Field("zgqpdsundqzzzcbq")
    email: str = Field("dimas.ngadinegaran@gmail.com")

config = Config()
