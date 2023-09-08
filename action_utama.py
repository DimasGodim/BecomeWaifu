from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Response
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, StreamingResponse
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
from model import logaudio, userdata
from database import init_db
from configs import config
from helper import pesan_response, request_audio, check_access_token_expired, check_premium, blob_to_wav

translator = Translator()
r = sr.Recognizer()
router = APIRouter(prefix='/action', tags=['action-utama-BW'])

@router.post("/change-voice/{speaker_id}/{language_used}")
async def change(speaker_id: int,language_used: str, access_token: str = Header(...), audio_file: UploadFile = File(...)):
    result = await check_access_token_expired(access_token=access_token)
    if result is True:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    elif result is False:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    else:
        user_id = result
        
    premium_response = await check_premium(user_id)
    if premium_response:
        return JSONResponse(premium_response, status_code=400)

    user_data = await logaudio.filter(user_id=user_id).order_by("-audio_id").first()
    if user_data:
        audio_id = user_data.audio_id + 1
    else:
        audio_id = 1  
    if audio_file.content_type not in ['audio/wav', 'audio/x-wav', 'audio/aiff', 'audio/x-aiff', 'audio/flac']:
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio = AudioSegment.from_file(audio_file.file, format="mp3")  # Adjust format as needed
        audio.export(temp_wav.name, format="wav")
        audio_file = temp_wav
    
    with sr.AudioFile(audio_file.file) as audio_file:
        audio_data = r.record(audio_file)
        transcript = r.recognize_google(audio_data, language=language_used)
        
    translation = translator.translate(transcript, dest='ja')
    request_audio(spaeker_id=speaker_id, text=translation.text)
    
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

@router.get("/get-audio-file/{audio_id}")
async def get_audio_file(audio_id: int, access_token: str = Header(...)):
    result = await check_access_token_expired(access_token=access_token)
    if result is True:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    elif result is False:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    else:
        user_id = result
    
    try:
        user = await userdata.filter(user_id=user_id).first()
        audio_data = await logaudio.filter(user_id=user_id, audio_id=audio_id).first()
        if audio_data:
            await blob_to_wav(data_audio=audio_data.audio_file)
            audio_file = 'voice.wav'
            return FileResponse(audio_file, media_type="audio/wav", filename='voice.wav', status_code=200)
        else:
            response = pesan_response(email=user.email, pesan=f'audio data dengan log-audio {audio_id} tidak ditemukan')
            return JSONResponse(response, status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-audio-streming/{audio_id}")
async def get_audio_streming(audio_id: int, access_token: str = Header(...)):
    result = await check_access_token_expired(access_token=access_token)
    if result is True:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    elif result is False:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    else:
        user_id = result

    try:
        user = await userdata.filter(user_id=user_id).first()
        audio_data = await logaudio.filter(user_id=user_id, audio_id=audio_id).first()
        if audio_data:
            await blob_to_wav(audio_data.audio_file)
            return Response(content='voice.wav', media_type='audio/wav')
        else:
            response = pesan_response(email=user.email, pesan=f'audio data dengan log-audio {audio_id} tidak ditemukan')
            return JSONResponse(response, status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-all-audio-data")
async def get_logaudio(access_token: str = Header(...)):
    result = await check_access_token_expired(access_token=access_token)
    if result is True:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    elif result is False:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    else:
        user_id = result
    
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

@router.delete("/delete-audio/{audio_id}")
async def delete_audio(audio_id: int, access_token: str = Header(...)):
    result = await check_access_token_expired(access_token=access_token)
    if result is True:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    elif result is False:
        return RedirectResponse(url=config.redirect_uri_page_masuk, status_code=401)
    else:
        user_id = result
    try:
        audio_data = await logaudio.filter(user_id=user_id, audio_id=audio_id).first()
        user = await userdata.filter(user_id=user_id).first()
        if audio_data:
            await audio_data.delete()
            # Mengambil semua audio dengan user_id yang sama dan audio_id lebih besar dari yang dihapus
            audio_to_update = await logaudio.filter(user_id=user_id, audio_id__gt=audio_id).all()
            # Mengupdate audio_id pada data yang lebih besar dari yang dihapus
            for audio in audio_to_update:
                audio.audio_id -= 1
                await audio.save()
            response = pesan_response(email=user.email, pesan=f'audio data dengan log-audio {audio_id} telah dihapus')
            return JSONResponse(response, status_code=200)
        else:
            response = pesan_response(email=user.email, pesan=f'audio data dengan log-audio {audio_id} tidak ditemukan')
            raise JSONResponse(response, status_code=404)
    
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        # Tangani eror lainnya dengan memberikan respons yang sesuai
        return JSONResponse(content={"error": str(err)}, status_code=500)
