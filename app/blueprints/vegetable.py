from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, g, redirect, render_template, request, url_for , abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Vegetable, VegetableCategory
from app.decorators import login_required

bp = Blueprint("vegetable", __name__)

@bp.route("/my/vegetables" , methods=["GET", "POST"])
@login_required
def my_vegetables():
    vegetables = db.session.scalars(
        db.select(Vegetable)
        .where(Vegetable.publisher_id == g.user.id)
        .order_by(Vegetable.id.desc())
    ).all()

    return render_template("my_vegetables.html", vegetables=vegetables)


@bp.post("/vegetable/<int:vegetable_id>/delete")
@login_required
def delete_vegetable(vegetable_id):
    vegetable = db.session.get(Vegetable, vegetable_id)

    if vegetable is None:
        abort(404)

    if vegetable.publisher_id != g.user.id:
        abort(403)

    try:
        db.session.delete(vegetable)
        db.session.commit()
        flash("删除成功", "success")
    except Exception:
        db.session.rollback()
        flash("删除失败，请稍后重试", "error")

    return redirect(url_for("vegetable.my_vegetables"))


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

@bp.route("/vegetable/<int:vegetable_id>/edit", methods=["GET", "POST"])
@login_required
def edit_vegetable(vegetable_id):
    vegetable = db.session.get(Vegetable, vegetable_id)

    if vegetable is None:
        abort(404)

    if vegetable.publisher_id != g.user.id:
        abort(403)

    if request.method == "GET":
        return render_template("edit_vegetable.html", vegetable=vegetable)

    picture = request.form.get("picture", "").strip()
    name = request.form.get("name", "").strip()
    price_raw = request.form.get("price", "").strip()
    category_id_raw = request.form.get("category", "").strip()
    description = request.form.get("content", "").strip()
    provider = request.form.get("provider", "").strip()
    mobile = request.form.get("mobile", "").strip()
    place = request.form.get("place", "").strip()

    if not picture:
        flash("请先上传图片", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if not name:
        flash("蔬菜名称不能为空", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if len(name) > 50:
        flash("蔬菜名称不能超过 50 个字符", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if not price_raw:
        flash("价格不能为空", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if not category_id_raw:
        flash("请选择分类", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if len(description) > 500:
        flash("描述不能超过 500 个字符", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    try:
        price = Decimal(price_raw)
    except (InvalidOperation, ValueError):
        flash("价格格式不正确", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    if price <= 0:
        flash("价格必须大于 0", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    try:
        category_id = int(category_id_raw)
    except ValueError:
        flash("分类参数不合法", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    category = db.session.get(VegetableCategory, category_id)
    if category is None:
        flash("所选分类不存在", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    vegetable.picture = picture
    vegetable.name = name
    vegetable.content = description
    vegetable.price = price
    vegetable.provider = provider
    vegetable.mobile = mobile
    vegetable.place = place
    vegetable.category_id = category_id

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("修改失败：该蔬菜名称已存在，请更换名称", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))
    except Exception:
        db.session.rollback()
        flash("修改失败，请稍后重试", "error")
        return redirect(url_for("vegetable.edit_vegetable", vegetable_id=vegetable.id))

    flash("修改成功", "success")
    return redirect(url_for("vegetable.my_vegetables"))