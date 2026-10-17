import json
import os
import smtplib
import ssl
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.utils import formataddr
import os, smtplib, ssl

from dotenv import load_dotenv
from flask import current_app

from routes import uploads
from services import sheet_service
from services import template_service


class  EmailService:
    def __init__(self):
        load_dotenv()
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_name = os.getenv("SENDER_NAME", "Easycertificate")

    def _upload_path(self, *parts):
        return os.path.join(current_app.root_path, "uploads", *parts)

    @staticmethod
    def _native_value(value):
        """Convert pandas/numpy scalar values returned by Excel readers."""
        if hasattr(value, "item"):
            try:
                value = value.item()
            except (ValueError, TypeError):
                pass
        return value

    def start_sending(self, body="testing", subject="certificate distribution"):
        sheet_path = self._upload_path("sheets", "recipients.xlsx")
        template_path = self._upload_path("templates", "template.pdf")

        if not os.path.exists(sheet_path):
            return {"success": False, "error": "Recipients sheet not uploaded"}, 400
        if not os.path.exists(template_path):
            return {"success": False, "error": "Template not uploaded"}, 400
        if not self.smtp_user or not self.smtp_password:
            return {"success": False, "error": "SMTP credentials not configured"}, 500

       

        try:
            
            xl_data = sheet_service.read_excel_file(sheet_path)
            sent = 0
            errors = []
            

            for id, name, email, date in zip(
                xl_data["ID"],
                xl_data["Name"],
                xl_data["Email"],
                xl_data["Date"],
            ):
                # read_excel_file may return numpy.int64/numpy.str_ values.
                # Normalize them before they reach template generation or JSON.
                name = self._native_value(name)
                email = self._native_value(email)
                recipient_id = self._native_value(id)
                date = self._native_value(date)

                name = "" if name is None else str(name)
                email = "" if email is None else str(email).strip()
                recipient_id = "" if recipient_id is None else str(recipient_id)
                date = "" if date is None else str(date)

                pdf = template_service.generate_pdf(
                    name, email, recipient_id, date, template_path,
                )
                

                
                personalized_body = (body or "").replace("{name}", name)
                result = self.send_email(
                    email, subject, personalized_body, attachments=[pdf]
                )
                

                if result.get("success"):
                    sent += 1
                else:
                    errors.append({
                        "email": email,
                        "error": str(result.get("error", "Email could not be sent")),
                    })

            print(f"Sent {sent} email(s), Failed: {len(errors)}")
            if sent == 0:
                return {
                    "success": False,
                    "error": "Failed to send all emails",
                    "details": errors,
                }, 500
            
            if os.path.exists(sheet_path):
                os.remove(sheet_path)
            if os.path.exists(template_path):
                os.remove(template_path)

            return {
                "success": True,
                "message": f"Sent {sent} email(s)",
                "failed": errors,
            }, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        msg = EmailMessage()
        msg["From"] = formataddr((self.sender_name, self.smtp_user))
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.set_content(body)                              # plain text
        if html_body:
            msg.add_alternative(html_body, subtype="html") # HTML version

        if attachments:
            if not isinstance(attachments, list):
                attachments = [attachments]

            for i, attachment in enumerate(attachments, start=1):
                filename = f"certificate_{i}.pdf"
                if isinstance(attachment, tuple):          # ("name.pdf", data)
                    filename, attachment = attachment

                if isinstance(attachment, (bytes, bytearray)):
                    file_data = bytes(attachment)
                elif hasattr(attachment, "read"):
                    file_data = attachment.read()
                    filename = os.path.basename(getattr(attachment, "name", filename))
                else:
                    with open(attachment, "rb") as f:
                        file_data = f.read()
                    filename = os.path.basename(attachment)

                msg.add_attachment(file_data, maintype="application",
                                subtype="pdf", filename=filename)

        # Create a new SMTP connection for every attempt. SMTP providers can
        # occasionally close an idle connection before send_message().
        last_error = None
        for attempt in range(3):
            try:
                context = ssl.create_default_context()
                if self.smtp_port == 465:
                    server = smtplib.SMTP_SSL(
                        self.smtp_host, self.smtp_port,
                        context=context, timeout=30,
                    )
                else:
                    server = smtplib.SMTP(
                        self.smtp_host, self.smtp_port, timeout=30,
                    )

                with server:
                    server.ehlo()
                    if self.smtp_port != 465:
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                return {"success": True, "message": "Email sent"}
            except smtplib.SMTPServerDisconnected as e:
                last_error = e
                if attempt < 2:
                    time.sleep(2)
            except Exception as e:
                return {"success": False, "error": f"{type(e).__name__}: {e}"}

        return {
            "success": False,
            "error": f"{type(last_error).__name__}: {last_error}",
        }