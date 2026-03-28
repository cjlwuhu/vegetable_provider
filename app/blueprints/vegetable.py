from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Vegetable, VegetableCategory
from app.decorators import login_required

bp = Blueprint("vegetable", __name__)


@bp.route("/pub", methods=["GET", "POST"])
@login_required
def pub():
    if request.method == "GET":
        return render_template("pub.html")

    picture = request.form.get("picture", "").strip()
    name = request.form.get("name", "").strip()
    price_raw = request.form.get("price", "").strip()
    category_id_raw = request.form.get("category", "").strip()
    description = request.form.get("content", "").strip()
    provider = request.form.get("provider" , "").strip()
    mobile = request.form.get("mobile" , "").strip()
    place = request.form.get("place" , "").strip()

    # 1. 基础非空校验
    if not picture:
        flash("请先上传图片", "error")
        return redirect(url_for("vegetable.pub"))

    if not name:
        flash("蔬菜名称不能为空", "error")
        return redirect(url_for("vegetable.pub"))

    if len(name) > 50:
        flash("蔬菜名称不能超过 50 个字符", "error")
        return redirect(url_for("vegetable.pub"))

    if not price_raw:
        flash("价格不能为空", "error")
        return redirect(url_for("vegetable.pub"))

    if not category_id_raw:
        flash("请选择分类", "error")
        return redirect(url_for("vegetable.pub"))

    if len(description) > 500:
        flash("描述不能超过 500 个字符", "error")
        return redirect(url_for("vegetable.pub"))

    # 2. 价格校验
    try:
        price = Decimal(price_raw)
    except (InvalidOperation, ValueError):
        flash("价格格式不正确", "error")
        return redirect(url_for("vegetable.pub"))

    if price <= 0:
        flash("价格必须大于 0", "error")
        return redirect(url_for("vegetable.pub"))

    # 3. 分类校验
    try:
        category_id = int(category_id_raw)
    except ValueError:
        flash("分类参数不合法", "error")
        return redirect(url_for("vegetable.pub"))

    category = db.session.get(VegetableCategory, category_id)
    if category is None:
        flash("所选分类不存在", "error")
        return redirect(url_for("vegetable.pub"))

    # 4. 写入数据库
    vegetable = Vegetable(
        category_id=category_id,
        picture=picture,
        name=name,
        content=description,
        price=price,
        provider=provider,
        mobile=mobile,
        place=place,
        publisher_id=g.user.id,
    )

    try:
        db.session.add(vegetable)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("发布失败：该蔬菜名称已存在，请更换名称", "error")
        return redirect(url_for("vegetable.pub"))
    except Exception:
        db.session.rollback()
        flash("发布失败，请稍后重试", "error")
        return redirect(url_for("vegetable.pub"))

    flash("发布成功", "success")
    return redirect(url_for("main.index"))
