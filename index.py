from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from googletrans import Translator
import speech_recognition as sr
import json

app = FastAPI()
translator = Translator()
r = sr.Recognizer()
hasil = "voice.wav"

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
    with open(hasil, 'wb') as file:
        file.write(response.content)

@app.post("/voice/{language_used}")
async def Translate(language_used: str, audio_file: UploadFile = File(...)):
    audio = audio.file
    with sr.AudioFile(audio) as audio_file:
            audio_data = r.record(audio_file)
            transcript = r.recognize_google(audio_data, language="id-ID")
            
    translation = translator.translate(transcript, dest='ja')
    request_audio(text=translation.text)
    result = {
        "transcript": transcript,
        "translation": translation.text
    }
    return JSONResponse (result)
    return FileResponse(hasil, media_type="audio/wav")