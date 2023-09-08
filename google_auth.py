from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests
import os
from configs import config
from model import userdata, access_token_data
from helper import create_access_token, access_token_response, credentials_to_dict

router = APIRouter(tags=['google-auth-login-regis'])
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

@router.get("/register")
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

@router.get("/login")
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

@router.get("/auth2callbackRegister")
async def auth2callback_register(request: Request, state: str):
    try:
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
            await create_access_token(user_id=user.user_id)
            response = await access_token_response(user)
            return JSONResponse(response, status_code=201)
        else:
            return RedirectResponse (config.redirect_uri_page_masuk, status_code=403)
    except ConnectionError as e:
        # Mengatasi kesalahan koneksi
        print(f"Kesalahan koneksi: {e}")
        return JSONResponse({"error": "Request Timed Out"}, status_code=500)

    
@router.get("/auth2callbackLogin")
async def auth2callback(request: Request, state: str):
    try:
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
            await create_access_token(user_id=user.user_id)
            response = await access_token_response(user)
            return JSONResponse(response, status_code=200)
    except ConnectionError as e:
        # Mengatasi kesalahan koneksi
        print(f"Kesalahan koneksi: {e}")
        return JSONResponse({"error": "Request Timed Out"}, status_code=500)
