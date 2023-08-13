import requests
from configs import config
from pydantic import BaseModel

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
    
def user_response(user):
    return {
        "user_id": str(user.user_id),
        "nama": user.nama,
        "email": user.email,
        "password": user.password,
        "akunbw": user.akunbw,
        "token": str(user.token),
        "status": user.status
    }

def pesan_response(email: str, pesan: str):
    return {
        'email':email,
        'pesan':pesan
    }