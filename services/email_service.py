import json
import os
import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import current_app

from routes import uploads
from services import sheet_service
from services import template_service


class EmailService:
    def __init__(self):
        load_dotenv()
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_name = os.getenv("SENDER_NAME", "Chalo")

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
        coords_path = self._upload_path("coordinates.json")

        if not os.path.exists(sheet_path):
            return {"success": False, "error": "Recipients sheet not uploaded"}, 400
        if not os.path.exists(template_path):
            return {"success": False, "error": "Template not uploaded"}, 400
        if not self.smtp_user or not self.smtp_password:
            return {"success": False, "error": "SMTP credentials not configured"}, 500

        coordinates = None
        if os.path.exists(coords_path):
            with open(coords_path, encoding="utf-8") as coords_file:
                coordinates = json.load(coords_file)

        try:
            
            xl_data = sheet_service.read_excel_file(sheet_path)
           
           
            
            
          
            sent = 0
            errors = []
            

            for name, email in zip(xl_data["Name"], xl_data["Email"]):
                # read_excel_file may return numpy.int64/numpy.str_ values.
                # Normalize them before they reach template generation or JSON.
                name = self._native_value(name)
                email = self._native_value(email)
                name = "" if name is None else str(name)
                email = "" if email is None else str(email).strip()
                
                pdf = template_service.generate_pdf(
                    name, email, template_path, coordinates=coordinates
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
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        if attachments:
            if not isinstance(attachments, list):
                attachments = [attachments]

            for attachment in attachments:
                file_data = attachment.read()
                attachment.seek(0)

                part = MIMEApplication(file_data, _subtype="pdf")
                filename = getattr(attachment, "filename", "certificate.pdf")
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
                )
                msg.attach(part)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            return {"success": True, "message": "Email sent"}
        except Exception as e:
            return {"success": False, "error": str(e)}


