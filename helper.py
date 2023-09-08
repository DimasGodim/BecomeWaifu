from ast import pattern
import requests
from configs import config
from pydantic import BaseModel
import bcrypt
import secrets
import pytz
import re
import io
from pydub import AudioSegment
from datetime import datetime, timedelta
from model import logaudio, userdata, access_token_data

def request_audio(text,spaeker_id:int):
    url = 'https://deprecatedapis.tts.quest/v2/voicevox/audio/'
    params = {
        'key': config.api_key_voicevox,
        'speaker': spaeker_id,
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

async def create_access_token(user_id: str):
    token = secrets.token_hex(16)
    waktu_basi = datetime.now(pytz.utc) + timedelta(minutes=1)
    save = access_token_data(access_token=token, waktu_basi=waktu_basi, user_id=user_id)
    await save.save()

async def check_access_token_expired(access_token: str):
    current_time = datetime.now(pytz.utc)
    data = await access_token_data.filter(access_token=access_token).first()
    
    if data:
        if data.waktu_basi <= current_time:
            await data.delete()
            return True
        else:
            return data.user_id
    else:
        return False

async def check_premium(user_id:str):
    user = await userdata.filter(user_id=user_id).first()
    if not user.premium:
        user_audio_count = await logaudio.filter(user_id=user_id).count()
        if user_audio_count >= 10:
            response = pesan_response(email=user.email, pesan="logaudio data anda telah mencapai limit. Upgrade ke plan premium atau hapus logaudio.")
            return response
    else:
        current_time = datetime.now()
        if user.waktu_basi_premium and user.waktu_basi_premium <= current_time:
            user.premium = False
            await user.save()
            response = pesan_response(email=user.email, pesan="Masa premium telah habis. Kembali ke versi gratis.")
            return response

async def access_token_response(user, password=None):
    user_id = user.user_id
    access_tokens = await access_token_data.filter(user_id=user_id).all()
    valid_access_tokens = []

    for data in access_tokens:
        is_valid = await check_access_token_expired(data.access_token)

        if not is_valid:
            continue

        valid_access_tokens.append(data)

    if valid_access_tokens:
        response_list = []

        for data in valid_access_tokens:
            response = {
                'access_token': str(data.access_token),
                'waktu_basi': str(data.waktu_basi),
                'data_user': {
                    "user_id": str(user.user_id),
                    "nama": user.nama,
                    "email": user.email,
                    "akunbw": user.akunbw,
                    "status": user.status
                }
            }

            if password is not None:
                response['data_user']['password'] = password

            response_list.append(response)

        return response_list
    else:
        return []

def validation_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return True
    else:
        return False

async def blob_to_wav(data_audio):
    audio = AudioSegment.from_file(io.BytesIO(data_audio), format="wav")
    output_file = 'voice.wav'
    audio.export(output_file, format='wav')
