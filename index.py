from fastapi import FastAPI, Request
from database import init_db
import action_utama
import bw_auth
import google_auth

# deklarasi nilai
app =  FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db(app)

app.include_router(action_utama.router)
app.include_router(bw_auth.router)
app.include_router(google_auth.router)

@app.get("/page-masuk")
async def root(request: Request):
 return ("masuk")

@app.get("/halaman-utama")
async def halaman_utama():
    return ("selamat datang")

# TODO: intergration with digital wallet