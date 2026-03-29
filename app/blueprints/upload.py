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



import os
import time
import uuid

from PIL import Image
from flask import Blueprint, current_app, g, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import PredictionRecord, VegetableCategory
from dlmodel import predict

from app.decorators import login_required
from flask import render_template

bp = Blueprint("upload", __name__)


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def allowed_mimetype(mimetype: str) -> bool:
    return mimetype in current_app.config["ALLOWED_IMAGE_MIMETYPES"]


def verify_image(file_storage) -> bool:
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

    if g.user is None:
        return jsonify({"result": False, "message": "请先登录后再上传"}), 401

    os.makedirs(current_app.config["MEDIA_DIR"], exist_ok=True)

    original_name = secure_filename(picture.filename)
    ext = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    picture_path = os.path.join(current_app.config["MEDIA_DIR"], filename)
    picture_url = f"/media/{filename}"

    try:
        picture.save(picture_path)

        start_time = time.perf_counter()
        category_name = predict(picture_path)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        if not category_name:
            record = PredictionRecord(
                user_id=g.user.id,
                image_path=picture_url,
                predicted_category_name=None,
                latency_ms=latency_ms,
                status="failed",
                error_message="图片识别失败，请更换图片重试",
            )
            db.session.add(record)
            db.session.commit()

            if os.path.exists(picture_path):
                os.remove(picture_path)

            return jsonify({"result": False, "message": "图片识别失败，请更换图片重试"}), 422

        category = db.session.scalar(
            db.select(VegetableCategory).where(VegetableCategory.name == category_name)
        )

        if category is None:
            record = PredictionRecord(
                user_id=g.user.id,
                image_path=picture_url,
                predicted_category_name=category_name,
                latency_ms=latency_ms,
                status="failed",
                error_message=f"识别成功，但未找到分类：{category_name}",
            )
            db.session.add(record)
            db.session.commit()

            if os.path.exists(picture_path):
                os.remove(picture_path)

            return jsonify({"result": False, "message": f"识别成功，但未找到分类：{category_name}"}), 422

        record = PredictionRecord(
            user_id=g.user.id,
            image_path=picture_url,
            predicted_category_name=category_name,
            latency_ms=latency_ms,
            status="success",
            error_message=None,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify(
            {
                "result": True,
                "message": "上传并识别成功",
                "category": {
                    "id": category.id,
                    "name": category.name,
                },
                "filename": filename,
                "picture_url": picture_url,
                "latency_ms": latency_ms,
            }
        )

    except Exception:
        db.session.rollback()

        try:
            record = PredictionRecord(
                user_id=g.user.id,
                image_path=picture_url,
                predicted_category_name=None,
                latency_ms=None,
                status="failed",
                error_message="图片上传失败，请稍后重试",
            )
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()

        if os.path.exists(picture_path):
            os.remove(picture_path)

        return jsonify({"result": False, "message": "图片上传失败，请稍后重试"}), 500


@bp.route("/media/<filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)



@bp.route("/my/predictions")
@login_required
def my_predictions():
    records = db.session.scalars(
        db.select(PredictionRecord)
        .where(PredictionRecord.user_id == g.user.id)
        .order_by(PredictionRecord.id.desc())
    ).all()

    return render_template("my_predictions.html", records=records)