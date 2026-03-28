import os
import uuid

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from app.extensions import db
from app.models import VegetableCategory
from dlmodel import predict

bp = Blueprint("upload", __name__)


@bp.post("/upload/picture")
def upload_picture():
    picture = request.files.get("picture")
    ext = picture.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    picture_path = os.path.join(current_app.config["MEDIA_DIR"], filename)
    picture.save(picture_path)

    category_name = predict(picture_path)
    category = db.session.scalar(
        db.select(VegetableCategory).where(VegetableCategory.name == category_name)
    )

    return jsonify(
        {
            "picture_path": picture_path,
            "result": True,
            "category": {
                "id": category.id,
                "name": category_name,
            },
            "filename": filename,
        }
    )


@bp.route("/media/<filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)
