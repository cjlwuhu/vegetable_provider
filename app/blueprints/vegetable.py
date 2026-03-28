from flask import Blueprint, g, redirect, render_template, request, flash

from app.decorators import login_required
from app.extensions import db
from app.models import Vegetable, VegetableCategory

bp = Blueprint("vegetable", __name__)


@bp.route("/pub", methods=["GET", "POST"])
@login_required
def pub():
    if request.method == "GET":
        categories = db.session.scalars(db.select(VegetableCategory)).all()
        return render_template("pub.html", categories=categories)

    category_id = request.form.get("category")
    picture = request.form.get("picture")
    name = request.form.get("name")
    content = request.form.get("content")
    price = request.form.get("price")
    place = request.form.get("place")
    provider = request.form.get("provider")
    mobile = request.form.get("mobile")

    if not picture:
        flash("请先上传图片", "error")
        return redirect("/pub")

    if not name:
        flash("蔬菜名称不能为空", "error")
        return redirect("/pub")

    if not price:
        flash("价格不能为空", "error")
        return redirect("/pub")

    vegetable = Vegetable(
        category_id=category_id,
        picture=picture,
        name=name,
        content=content,
        price=price,
        provider=provider,
        mobile=mobile,
        place=place,
        publisher_id=g.user.id,
    )
    db.session.add(vegetable)
    db.session.commit()

    return redirect("/")
