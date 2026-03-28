import os
import uuid

from PIL import Image
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import VegetableCategory
from dlmodel import predict

bp = Blueprint("upload", __name__)


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def allowed_mimetype(mimetype: str) -> bool:
    return mimetype in current_app.config["ALLOWED_IMAGE_MIMETYPES"]


def verify_image(file_storage) -> bool:
    """
    校验是否为真实图片，而不是仅仅后缀伪装。
    """
    try:
        file_storage.stream.seek(0)
        image = Image.open(file_storage.stream)
        image.verify()
        file_storage.stream.seek(0)
        return True
    except Exception:
        file_storage.stream.seek(0)
        return False


@bp.post("/upload/picture")
def upload_picture():
    picture = request.files.get("picture")

    if picture is None:
        return jsonify({"result": False, "message": "未检测到上传文件"}), 400

    if not picture.filename:
        return jsonify({"result": False, "message": "文件名不能为空"}), 400

    if not allowed_file(picture.filename):
        return jsonify({"result": False, "message": "仅支持 jpg、jpeg、png、webp 图片"}), 400

    if not allowed_mimetype(picture.mimetype):
        return jsonify({"result": False, "message": "文件类型不合法"}), 400

    if not verify_image(picture):
        return jsonify({"result": False, "message": "上传文件不是有效图片"}), 400

    os.makedirs(current_app.config["MEDIA_DIR"], exist_ok=True)

    original_name = secure_filename(picture.filename)
    ext = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    picture_path = os.path.join(current_app.config["MEDIA_DIR"], filename)

    try:
        picture.save(picture_path)

        category_name = predict(picture_path)
        if not category_name:
            if os.path.exists(picture_path):
                os.remove(picture_path)
            return jsonify({"result": False, "message": "图片识别失败，请更换图片重试"}), 422

        category = db.session.scalar(
            db.select(VegetableCategory).where(VegetableCategory.name == category_name)
        )

        if category is None:
            if os.path.exists(picture_path):
                os.remove(picture_path)
            return jsonify({"result": False, "message": f"识别成功，但未找到分类：{category_name}"}), 422

        return jsonify(
            {
                "result": True,
                "message": "上传并识别成功",
                "category": {
                    "id": category.id,
                    "name": category.name,
                },
                "filename": filename,
                "picture_url": f"/media/{filename}",
            }
        )

    except Exception:
        if os.path.exists(picture_path):
            os.remove(picture_path)
        return jsonify({"result": False, "message": "图片上传失败，请稍后重试"}), 500


@bp.route("/media/<filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)