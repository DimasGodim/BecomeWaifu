from fastapi import FastAPI, File, UploadFile, HTTPException, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from tortoise.exceptions import DoesNotExist
import requests
import secrets
import os
import speech_recognition as sr
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googletrans import Translator
from model import logaudio, userdata  
from database import init_db
from configs import config
from helper import request_audio, credentials_to_dict, user_response, pesan_response
from send_email import send_email

# deklarasi nilai
app =  FastAPI()
translator = Translator()
r = sr.Recognizer()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


@app.on_event("startup")
async def startup_event():
    init_db(app)

@app.post("/change-voice/{user_id}/{language_used}")
async def change(user_id: str, language_used: str, audio_file: UploadFile = File(...)):
    user = await userdata.filter(user_id=user_id).exists()
    if not user:
        raise HTTPException(status_code=404, detail="Item not found")
    user_data = await logaudio.filter(user_id=user_id).order_by("-audio_id").first()
    if user_data:
        audio_id = user_data.audio_id + 1
    else:
        audio_id = 1  
    with sr.AudioFile(audio_file.file) as audio_file:
        audio_data = r.record(audio_file)
        transcript = r.recognize_google(audio_data, language=language_used)
    translation = translator.translate(transcript, dest='ja')
    request_audio(text=translation.text)
    with open("voice.wav", "rb") as file:
        audio_get = file.read()
    save = logaudio(audio_id=audio_id, user_id=user_id, transcript=transcript, translate=translation.text, audio_file=audio_get)
    await save.save()  
    data = {
        'user_id': user_id,
        'id_audio': audio_id,
        'transcript': transcript,
        'translation': translation.text 
    }
    return JSONResponse(data)

@app.get("/get-audio/{user_id}/{audio_id}")
async def get_audio(user_id: str, audio_id: int):
    try:
        audio_data = await logaudio.filter(user_id=user_id, audio_id=audio_id).first()
        if audio_data:
            return Response(content=audio_data.audio_file, media_type="audio/wav")
        else:
            raise HTTPException(status_code=404, detail="Audio not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def auth2callback_register(request: Request, state: str):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['email', 'profile'],  
        state=state
    )
    flow.redirect_uri = config.redirect_uri_register
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    access_token = credentials.token

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")
    nama = user_info.get("name")

    existing_user = await userdata.filter(email=email).first()
    if not existing_user:
        save = userdata(nama=nama, email=email, status=True, token=access_token)
        await save.save()
        user = await userdata.filter(email=email).first()
        response = user_response(user)
        return JSONResponse(response)
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
    access_token = credentials.token

    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
    user_info_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()
    email = user_info.get("email")

    existing_user = await userdata.filter(email=email).first()
    if not existing_user:
        return RedirectResponse(config.redirect_uri_page_masuk)
    else:
        user = await userdata.filter(email=email).first()
        response =user_response(user)
        return JSONResponse(response)
        
@app.get("/login-bw/{email}/{passowrd}")
async def login_bw(email: str, password: str):
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.akunbw is False: # email sudah pernah terdaftar akun BW
            return RedirectResponse (config.redirect_uri_page_masuk)
        else: # email tersebut telah terdaftar ke akun BecomeWaifu
            response = user_response(user)
            return JSONResponse(response)
    else: # belum pernah daftar sama sekali
        return RedirectResponse (config.redirect_uri_page_masuk)

@app.get("/register-bw/{email}")
async def create_account(email: str):
    token_konfirmasi = secrets.token_hex(16)
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.ban: # cek apakah dia di ban
            return("anda di ban")
        else:
            if user.password is None: # email sudah pernah terdaftar melalui google auth namun belum pernah membuat akun BW
                user.token = token_konfirmasi
                await user.save()
                send_email(target_email=email, token=token_konfirmasi)
                response = pesan_response(email=email,pesan="token konfirmasi telah dikirimkan")
                return JSONResponse(response)
            else: # email tersebut telah terdaftar ke akun BecomeWaifu
                return RedirectResponse(config.redirect_uri_page_masuk)
    else: # belum pernah daftar sama sekali
        save = userdata(email=email, token=token_konfirmasi)
        await save.save()
        send_email(target_email=email, token=token_konfirmasi)
        response = pesan_response(email=email, pesan="token konfirmasi telah dikirimakan")
        return JSONResponse(response)

@app.post("/simpan-pengguna-bw")
async def proses_pengguna(email: str, password: str, token: str):
    user = await userdata.filter(email=email).first()
        
    if user.token and user.token == token:
        # Token cocok dengan pengguna
        if not user.status:
            # Akun pengguna tidak aktif
            user.password = password  # Setel kata sandi baru
            user.status = True  # Setel status menjadi Aktif
            user.akunbw = True  # Setel akunbw menjadi Aktif
            user.token = None  # Hapus token
            await user.save()
            user_data = user_response(user)
            return JSONResponse(user_data)
        else:
            # Akun pengguna aktif, update kata sandi dan akunbw
            user.password = password  # Setel kata sandi baru
            user.akunbw = True  # Setel akunbw menjadi Aktif
            user.token = None  # Hapus token
            await user.save()
            user_data = user_response(user)
            return JSONResponse(user_data)
    else:
        # Token tidak cocok dengan pengguna
        if user.status:
            # Akun pengguna aktif, hapus token
            user.token = None  # Hapus token
            await user.save()
            user_data = user_response(user)
            response = pesan_response(email=email, pesan="token konfirmasi yang anda masukan salah")
        else:
            # Akun pengguna tidak aktif, hapus data pengguna
            await user.delete()  # Hapus data pengguna
            response = pesan_response(email=email, pesan="token konfirmasi yang anda masukan salah")
            return JSONResponse(response)

@app.get("/page-masuk")
async def root(request: Request):
 return ("masuk")

@app.get("/halaman-utama")
async def halaman_utama():
    return ("selamat datang")
# kekurangan simpan access_token ke session
# tampilkan user_id dan tampilkan data milik user

# test endpoint
@app.post("/add-audio/{user_id}")
async def add_audio(user_id: str):
    # Check if the user exists in userdata table
    user_exists = await userdata.filter(user_id=user_id).exists()

    if not user_exists:
        return {"message": f"User with user_id {user_id} not found"}

    existing_audio = await logaudio.filter(user_id=user_id).order_by("-audio_id").first()

    if existing_audio:
        new_audio_id = existing_audio.audio_id + 1
    else:
        new_audio_id = 1

    new_audio = logaudio(audio_id=new_audio_id, user_id=user_id, transcript="yjtyjuj", translate="jytjytjytj", audio_file=b"")
    await new_audio.save()
    
    return {"message": f"Audio with audio_id {new_audio_id} created for user_id {user_id}"}



