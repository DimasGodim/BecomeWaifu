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

    subject = "Konfirmasi Token untuk Aplikasi BecomeWaifu"
    sender_name = "Tim BecomeWaifu"
    sender_email = "no-reply@becomewaifu.com"  # Email dari domain aplikasi Anda
    
    # Pesan dalam format HTML
    message_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background-color: #f4f4f4; padding: 20px;">
            <h2 style="color: #333;">{subject}</h2>
            <p>Dear User,</p>
            <p>Thank you for choosing BecomeWaifu. Here is your confirmation token:</p>
            <p style="font-size: 18px; background-color: #ddd; padding: 10px;">{token}</p>
            <p>Please use this token to access our features and verify your identity in the BecomeWaifu app.</p>
            <p>If you did not initiate this request, please disregard this message. Thank you for your support!</p>
            <p style="margin-top: 20px;">Best regards,</p>
            <p>{sender_name}</p>
        </div>
    </body>
    </html>
    """

    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = target_email
    msg['Subject'] = subject

    # Set jenis konten email ke HTML
    msg.attach(MIMEText(message_body, 'html'))
    
    try:
        server = smtplib.SMTP(SERVER, PORT)
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.sendmail(sender_email, target_email, msg.as_string())
        print('Email berhasil dikirim!')
    except Exception as e:
        print('Terjadi kesalahan:', str(e))
    finally:
        server.quit()
