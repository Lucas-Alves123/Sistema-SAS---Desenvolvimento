import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# From config
MAIL_HOST = "antispamout.ati.pe.gov.br"
MAIL_PORT = 587
MAIL_USERNAME = "dgiis.ses"
MAIL_PASSWORD = "$35dG!1s"

try:
    print("Connecting to SMTP...")
    server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    server.set_debuglevel(1)
    
    print("Starting TLS...")
    server.starttls()
    
    print("Logging in...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    print("Login successful.")
    server.quit()
except Exception as e:
    print(f"SMTP Error: {e}")
