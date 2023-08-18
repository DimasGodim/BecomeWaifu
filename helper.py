import requests
from configs import config
from pydantic import BaseModel
import bcrypt
import secrets
from datetime import datetime, timedelta

def request_audio(text):
    url = 'https://deprecatedapis.tts.quest/v2/voicevox/audio/'
    params = {
        'key': config.api_key_voicevox,
        'speaker': '0',
        'pitch': '0',
        'intonationScale': '1',
        'speed': '1',
        'text': text
    }

    response = requests.get(url, params=params)
    with open('voice.wav', 'wb') as file:
        file.write(response.content)

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    
def user_response(user, password=None):
    response = {
        "user_id": str(user.user_id),
        "nama": user.nama,
        "email": user.email,
        "akunbw": user.akunbw,
        "token": str(user.token),
        "waktu_basi": str(user.waktu_basi),
        "status": user.status
    }
    
    if password is not None:
        response["password"] = password
    
    return response

def pesan_response(email: str, pesan: str):
    return {
        'email':email,
        'pesan':pesan
    }

def check_password(password: str, user):
    bytes = password.encode('utf-8')
    password_data = user.password
    result = bcrypt.checkpw(bytes, password_data)
    return result

def set_password(password: str):
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hash = bcrypt.hashpw(bytes, salt)
    return hash

async def create_token(user):
    token = secrets.token_hex(16)
    waktu_basi = datetime.now() + timedelta(hours=8)
    user.token = token
    user.waktu_basi = waktu_basi
    await user.save()

async def check_token_expired(user):
    current_time = datetime.now()
    if user.waktu_basi <= current_time:
        user.token = None  
        await user.save()
        return True
    else:
        return False
