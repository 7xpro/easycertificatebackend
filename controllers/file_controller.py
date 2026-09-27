import json
import os

from flask import current_app

from services.email_service import EmailService


class FileController:
    def __init__(self, file_service):
        self.file_service = file_service

    def template_file(self, template_file):
        return self.file_service.save_file(
            template_file, subdir="templates", save_as="template.pdf"
        )

    def userList_file(self, xlsx_file):
        return self.file_service.save_file(
            xlsx_file, subdir="sheets", save_as="recipients.xlsx"
        )

    def template_cordinates(self, cordinates):
        template_cordinates = cordinates.get("cordinates", {})
        coords_path = os.path.join(
            current_app.root_path, "uploads", "coordinates.json"
        )
        os.makedirs(os.path.dirname(coords_path), exist_ok=True)
        with open(coords_path, "w", encoding="utf-8") as coords_file:
            json.dump(template_cordinates, coords_file)

        return {"cordinates": template_cordinates}, 200

    def start_sending(self, body, subject):
       
        response, status_code = EmailService().start_sending(body, subject)
       
        return response, status_code
        
        
        

  