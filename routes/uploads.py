
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from controllers.file_controller import FileController
from services.file_service import FileService
from services.sheet_service import read_excel_file


routes_bp = Blueprint("upload", __name__)
file_controller = FileController(FileService())

@routes_bp.route("/template", methods=["POST"])
@jwt_required()
def upload_template():
    if "file" not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    response, status_code = file_controller.template_file(file)
    return jsonify(response), status_code


@routes_bp.route("/sheet", methods=["POST"])
@jwt_required()
def upload_sheet():
    if "file" not in request.files:
        return jsonify({"error": "No file found"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    response, status_code = file_controller.userList_file(file)
    if status_code==201:
        response=read_excel_file("./uploads/sheets/recipients.xlsx")
        return jsonify(response), 201


@routes_bp.route("/cordinates", methods=["POST"])
@jwt_required()
def upload_cordinates():
  
    cordinates = request.get_json(silent=True) or {}

    response, status_code = file_controller.template_cordinates(cordinates)
    return jsonify(response), status_code



@routes_bp.route("/test", methods=["POST"])
@jwt_required()
def start_sending():
    data = request.get_json(silent=True) or {}
    body = data.get("body")
    subject = data.get("subject")
  
    response, status_code = file_controller.start_sending(body, subject)
    return jsonify(response), status_code



    
    