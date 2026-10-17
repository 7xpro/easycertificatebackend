import os, smtplib, ssl
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("SMTP_HOST", "smtp.gmail.com")
user = os.getenv("SMTP_USER")
pw = os.getenv("SMTP_PASSWORD")
print(repr(host), repr(os.getenv("SMTP_PORT")), repr(user), "password length:", len(pw or ""))

ctx = ssl.create_default_context()

for port in (465, 587):
    print(f"\n--- port {port} ---")
    try:
        if port == 465:
            s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=20)
        else:
            s = smtplib.SMTP(host, port, timeout=20)
        s.set_debuglevel(1)
        s.ehlo()
        if port == 587:
            s.starttls(context=ctx)
            s.ehlo()
        s.login(user, pw)
        print("LOGIN OK")
        s.quit()
    except Exception as e:
        print("FAILED:", type(e).__name__, e)