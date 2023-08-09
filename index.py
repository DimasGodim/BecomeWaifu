from fastapi import FastAPI, File, UploadFile, HTTPException, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
import requests
import os
import speech_recognition as sr
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googletrans import Translator
from model import logaudio, userdata  
from database import init_db
from configs import config

# deklarasi nilai
app =  FastAPI()
translator = Translator()
r = sr.Recognizer()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

#  function 
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

@app.on_event("startup")
async def startup_event():
    init_db(app)

@app.post("/change-voice/{user_id}/{language_used}")
async def change(user_id: str, language_used: str, audio_file: UploadFile = File(...)):
    with sr.AudioFile(audio_file.file) as audio_file:
        audio_data = r.record(audio_file)
        transcript = r.recognize_google(audio_data, language=language_used)
    translation = translator.translate(transcript, dest='ja')
    request_audio(text=translation.text)
    with open("voice.wav", "rb") as file:
        audio_get = file.read()
    save = logaudio(user_id=user_id, transcript=transcript, translate=translation.text, audio_file=audio_get)
    await save.save()  
    data = {
        'transcript': transcript,
        'translation': translation.text,
        'id_audio': str(save.audio_id)  
    }

    return JSONResponse(data)  

@app.get("/get-audio/{audio_id}")
async def get(audio_id: str):
    data = await logaudio.get(audio_id = audio_id)
    if data:
        return Response(content=data.audio_file, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="Audio not found")

@app.get("/register")
async def daftar():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@app.get("/login")
async def daftar():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile']  
    )
    flow.redirect_uri = config.redirect_uri_login
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@app.get("/auth2callbackRegister")
async def auth2callback(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile'],  
        state=state
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    creds = credentials_to_dict(credentials)

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {credentials.token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")
    nama = user_info.get("name")

    existing_user = await userdata.filter(email=email).first()
    if not existing_user:
        save = userdata(nama=nama, email=email)
        await save.save()
        return JSONResponse(creds)
    else:
        return RedirectResponse (config.redirect_uri_page_masuk)
    
@app.get("/auth2callbackLogin")
async def auth2callback(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile'],  
        state=state
    )
    flow.redirect_uri = config.redirect_uri_login
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    creds = credentials_to_dict(credentials)

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {credentials.token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")
    nama = user_info.get("name")

    existing_user = await userdata.filter(email=email).first()
    if not existing_user:
        return RedirectResponse (config.redirect_uri_page_masuk)
    else:
        return JSONResponse(creds)

@app.get("/login-bw/{email}/{passowrd}")
async def login_bw(email: str, password: str):
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.password is None: # email sudah pernah terdaftar melalui google auth namun belum pernah membuat akun BW
            return RedirectResponse (config.redirect_uri_page_masuk)
        else: # email tersebut telah terdaftar ke akun BecomeWaifu
            user_id = str(user.user_id)
            return JSONResponse (
                {
                    'email':email,
                    'user_id':user_id,
                    'pesan':'selamat datang'
                }
            )
    else: # belum pernah daftar sama sekali
        return RedirectResponse (config.redirect_uri_page_masuk)

@app.get("/register-bw/{email}/{password}")
async def create_acoount(email: str, password: str):
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.password is None: # email sudah pernah terdaftar melalui google auth namun belum pernah membuat akun BW
            user.password = password
            await user.save()
            return JSONResponse(
                {
                    'email':email,
                    'pesan':'akun sudah dibuat silahkan login'
                })
        else: # email tersebut telah terdafatr ke akun BecomeWaifu
            return RedirectResponse (config.redirect_uri_page_masuk)
    else: # belum pernah daftar sama sekali
        new_user = userdata(email=email, password=password)
        await new_user.save()
        return JSONResponse(
            {
            'email':email,
            'pesan':'akun sudah dibuat silahkan login'
            }
            )

@app.get("/")
async def root():
    return ("silahkan login atau regis terlebih dahulu")

@app.get("/halaman-utama")
async def halaman_utama(request: Request):
    return ("selamat datang")

# kekurangan simpan access_token ke session
# tampilkan user_id dan tampilkan data milik user