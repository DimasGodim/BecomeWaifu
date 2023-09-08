from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import secrets
from model import userdata
from send_email import send_email
from configs import config
from helper import create_access_token, check_password, access_token_response, pesan_response, user_response, set_password, validation_email

router = APIRouter(prefix='/bw-auth', tags=['bw-autentikasi-login-regis'])

@router.get("/login/{email}")
async def login_bw(email: str, password: str):
    user = await userdata.filter(email=email).first()

    if user: # cek apakah email ada atau tidak
        if user.akunbw is False: # email belum terdaftar akun BW
            return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)
        else: # email tersebut telah terdaftar ke akun BecomeWaifu
            if not check_password(password, user):
                raise HTTPException(status_code=401, detail="Invalid password")
            await create_access_token(user_id = user.user_id)
            response = await access_token_response(user=user,password=password)
            return JSONResponse(response, status_code=200)
    else: # belum pernah daftar sama sekali
        return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)

@router.get("/register/{email}")
async def create_account(email: str):
    token_konfirmasi = secrets.token_hex(16)
    user = await userdata.filter(email=email).first()

    validasi_email = validation_email(email)
    
    if validasi_email is False:
        response = pesan_response(email=email, pesan="email yang anda masukan tidak valid")
        return JSONResponse(response, status_code=400)

    if user: # cek apakah email ada atau tidak
        if user.ban: # cek apakah dia di ban
            pesan_response(email=email,pesan="anda di ban")
            return JSONResponse(pesan_response, status_code=403)
        else:
            if user.password is None: # email sudah pernah terdaftar melalui google auth namun belum pernah membuat akun BW
                user.token_konfirmasi = token_konfirmasi
                await user.save()
                send_email(target_email=email, token=token_konfirmasi)
                response = pesan_response(email=email,pesan="token konfirmasi telah dikirimkan")
                return JSONResponse(response, status_code=200)
            else: # email tersebut telah terdaftar ke akun BecomeWaifu
                return RedirectResponse(config.redirect_uri_page_masuk, status_code=403)
    else: # belum pernah daftar sama sekali
        save = userdata(email=email, token_konfirmasi=token_konfirmasi)
        await save.save()
        send_email(target_email=email, token=token_konfirmasi)
        response = pesan_response(email=email, pesan="token konfirmasi telah dikirimakan")
        return JSONResponse(response, status_code=200)

@router.post("/simpan-pengguna")
async def proses_pengguna(email: str, password: str, token: str):
    user = await userdata.filter(email=email).first()
        
    if user:
        if user.token_konfirmasi and user.token_konfirmasi == token:
            # Token cocok dengan pengguna
            if not user.status:
                # Akun pengguna tidak aktif
                user.password = set_password(password=password)  # Setel kata sandi baru
                user.status = True  # Setel status menjadi Aktif
                user.akunbw = True  # Setel akunbw menjadi Aktif
                user.token_konfirmasi = None  # Hapus token
                await user.save()
                user_data = user_response(user=user, password=password)
                return JSONResponse(user_data, status_code=201)
            else:
                # Akun pengguna aktif, update kata sandi dan akunbw
                user.password = set_password(password=password)  # Setel kata sandi baru
                user.akunbw = True  # Setel akunbw menjadi Aktif
                user.token_konfirmasi = None  # Hapus token
                await user.save()
                user_data = user_response(user=user, password=password)
                return JSONResponse(user_data, status_code=201)
        else:
            # Token tidak cocok dengan pengguna
            if user.status:
                # Akun pengguna aktif, hapus token
                user.token_konfirmasi = None  # Hapus token
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
