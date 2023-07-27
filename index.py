from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.responses import JSONResponse
import requests
import speech_recognition as sr
from googletrans import Translator
from model import logaudio  
from database import init_db
from configs import config

app =  FastAPI()
translator = Translator()
r = sr.Recognizer()

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

@app.post("/change-voice/{language_used}")
async def change(language_used: str, audio_file: UploadFile = File(...)):
    with sr.AudioFile(audio_file.file) as audio_file:
        audio_data = r.record(audio_file)
        transcript = r.recognize_google(audio_data, language=language_used)
    translation = translator.translate(transcript, dest='ja')
    request_audio(text=translation.text)
    with open("voice.wav", "rb") as file:
        audio_get = file.read()
    save = logaudio(transcript=transcript, translate=translation.text, audio_file=audio_get)
    await save.save()  
    data = {
        'transcript': transcript,
        'translation': translation.text,
        'id_audio': str(save.id)  
    }

    return JSONResponse(data)  

@app.get("/get-audio/{audio_id}")
async def get(audio_id: str):
    data = await logaudio.get(id = audio_id)
    if data:
        return Response(content=data.audio_file, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="Audio not found")