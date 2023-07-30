# BW Project(BecomeWaifu)
Project Change Your Voice to Japanese Anime Girl (Become Waifu If Your Waifu Is Not Real) :)
# SYARAT 
1. api-key VoiceVox in (https://voicevox.su-shiki.com/su-shikiapis/)
2. MySQL database
# LANGKAH PENGGUNAAN
1. buat virtual env dan aktifkan
2. install syarat dengan perintah (pip install -r syarat.txt)
2. setting configs.py with Your VoiceVox API and your database link
3. jalankan perintah (aerich init -t database.TORTOISE_ORM)
4. jalankan perintah (aerich init-db)
5. jalankan program (uvicorn index:app --reload)
