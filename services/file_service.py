import os

from flask import current_app
from werkzeug.utils import secure_filename


class FileService:
    def save_file(self, upload_file, subdir="uploads", save_as=None):
        if upload_file is None or upload_file.filename == "":
            return {"error": "No selected file"}, 400

        upload_root = os.path.join(current_app.root_path, "uploads", subdir)
        os.makedirs(upload_root, exist_ok=True)

        filename = save_as or secure_filename(upload_file.filename)
        file_path = os.path.join(upload_root, filename)
        upload_file.save(file_path)

        return {
            "message": "File uploaded successfully",
            "filename": filename,
        }, 201
