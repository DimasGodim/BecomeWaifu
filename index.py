from fastapi import FastAPI, File, UploadFile, HTTPException, Response, Request, Header
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
from helper import request_audio, credentials_to_dict, user_response, pesan_response, set_password, check_password, create_token, check_token_expired
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
        raise HTTPException(status_code=404, detail="user not found")
    is_expired = await check_token_expired(user)
    if is_expired:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    
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
    return JSONResponse(data, status_code=200)

@app.get("/get-audio/{user_id}/{audio_id}")
async def get_audio(user_id: str, audio_id: int):
    user = await userdata.filter(user_id=user_id).exists()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    is_expired = await check_token_expired(user)
    if is_expired:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    
    try:
        audio_data = await logaudio.filter(user_id=user_id, audio_id=audio_id).first()
        if audio_data:
            return Response(content=audio_data.audio_file, media_type="audio/wav")
        else:
            raise HTTPException(status_code=404, detail="Audio not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get-all-audio-data/{user_id: str}")
async def get_logaudio(user_id: str):
    user = await userdata.filter(user_id=user_id).exists()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    is_expired = await check_token_expired(user)
    if is_expired:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    
    user_data = await logaudio.filter(user_id=user_id).all()
    if user_data:
        result = []
        for logaudio_entry in user_data:
            logaudio_data = {
                "user_id": logaudio_entry.user_id,
                "audio_id": logaudio_entry.audio_id,
                "user_id": logaudio_entry.user_id,
                "transcript": logaudio_entry.transcript,
                "translate": logaudio_entry.translate
            }
            result.append(logaudio_data)
        return JSONResponse(result, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="No logaudio data found")

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
        save = userdata(nama=nama, email=email, status=True)
        await save.save()
        user = await userdata.filter(email=email).first()
        await create_token(user)
        response = user_response(user)
        return JSONResponse(response, status_code=201)
    else:
        return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)
    
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
        return RedirectResponse(config.redirect_uri_page_masuk, status_code=405)
    else:
        user = await userdata.filter(email=email).first()
        await create_token(user)
        response =user_response(user)
        return JSONResponse(response, status_code=200)
        
@app.get("/login-bw/{email}/{passowrd}")
async def login_bw(email: str, password: str):
    user = await userdata.filter(email=email).first()
    await create_token(user)

    if user: # cek apakah email ada atau tidak
        if not check_password(password, user):
            raise HTTPException(status_code=401, detail="Invalid email or password")


        if user.akunbw is False: # email belum terdaftar akun BW
            return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)
        else: # email tersebut telah terdaftar ke akun BecomeWaifu
            response = user_response(user=user,password=password)
            return JSONResponse(response, status_code=200)
    else: # belum pernah daftar sama sekali
        return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)

@app.get("/register-bw/{email}")
async def create_account(email: str):
    token_konfirmasi = secrets.token_hex(16)
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.ban: # cek apakah dia di ban
            pesan_response(email=email,pesan="anda di ban")
            return JSONResponse(pesan_response, status_code=403)
        else:
            if user.password is None: # email sudah pernah terdaftar melalui google auth namun belum pernah membuat akun BW
                user.token = token_konfirmasi
                await user.save()
                send_email(target_email=email, token=token_konfirmasi)
                response = pesan_response(email=email,pesan="token konfirmasi telah dikirimkan")
                return JSONResponse(response, status_code=200)
            else: # email tersebut telah terdaftar ke akun BecomeWaifu
                return RedirectResponse(config.redirect_uri_page_masuk, status_code=403)
    else: # belum pernah daftar sama sekali
        save = userdata(email=email, token=token_konfirmasi)
        await save.save()
        send_email(target_email=email, token=token_konfirmasi)
        response = pesan_response(email=email, pesan="token konfirmasi telah dikirimakan")
        return JSONResponse(response, status_code=200)

@app.post("/simpan-pengguna-bw")
async def proses_pengguna(email: str, password: str, token: str):
    user = await userdata.filter(email=email).first()
        
    if user:
        if user.token and user.token == token:
            # Token cocok dengan pengguna
            if not user.status:
                # Akun pengguna tidak aktif
                user.password = set_password(password=password)  # Setel kata sandi baru
                user.status = True  # Setel status menjadi Aktif
                user.akunbw = True  # Setel akunbw menjadi Aktif
                user.token = None  # Hapus token
                await user.save()
                user_data = user_response(user=user, password=password)
                return JSONResponse(user_data, status_code=201)
            else:
                # Akun pengguna aktif, update kata sandi dan akunbw
                user.password = set_password(password=password)  # Setel kata sandi baru
                user.akunbw = True  # Setel akunbw menjadi Aktif
                user.token = None  # Hapus token
                await user.save()
                user_data = user_response(user=user, password=password)
                return JSONResponse(user_data, status_code=201)
        else:
            # Token tidak cocok dengan pengguna
            if user.status:
                # Akun pengguna aktif, hapus token
                user.token = None  # Hapus token
                await user.save()
                user_data = user_response(user=user)
                response = pesan_response(email=email, pesan="token konfirmasi yang anda masukan salah")
                return JSONResponse(response, status_code=404)
            else:
                # Akun pengguna tidak aktif, hapus data pengguna
                await user.delete()  # Hapus data pengguna
                response = pesan_response(email=email, pesan="token konfirmasi yang anda masukan salah")
                return JSONResponse(response, status_code=404)
    else:
        # User tidak ditemukan
        response = pesan_response(email=email, pesan="Pengguna tidak ditemukan")
        return JSONResponse(response, status_code=404)

@app.get("/page-masuk")
async def root(request: Request):
 return ("masuk")

@app.get("/halaman-utama")
async def halaman_utama():
    return ("selamat datang")