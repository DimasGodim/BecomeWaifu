import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configs import config  


SERVER = 'smtp.gmail.com'
PORT = 587
MY_EMAIL = config.email
MY_PASSWORD = config.password_email

def send_email(target_email: str, token: str):
    msg = MIMEMultipart()
    pesan = f"""
Halo,

Terima kasih telah menggunakan aplikasi kami, BecomeWaifu. Berikut adalah token konfirmasi Anda:

Token Konfirmasi: {token}

Harap gunakan token ini untuk mengakses fitur-fitur kami dan memverifikasi identitas Anda di aplikasi BecomeWaifu.

Jika Anda tidak mengirimkan permintaan ini, harap abaikan pesan ini. Terima kasih atas dukungan Anda!

Salam,
Tim BecomeWaifu
"""
    msg['From'] = MY_EMAIL
    msg['To'] = target_email
    msg['Subject'] = "Konfirmasi Token untuk Aplikasi BecomeWaifu"
    msg.attach(MIMEText(pesan, 'plain'))
    
    try:
        server = smtplib.SMTP(SERVER, PORT)
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.sendmail(MY_EMAIL, target_email, msg.as_string())
        print('Email berhasil dikirim!')
    except Exception as e:
        print('Terjadi kesalahan:', str(e))
    finally:
        server.quit()