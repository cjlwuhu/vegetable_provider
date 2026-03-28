from flask import Blueprint, render_template, request

from app.extensions import db
from app.models import Vegetable

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    category_id = request.args.get("category_id", type=int)

    if category_id:
        stmt = db.select(Vegetable).where(Vegetable.category_id == category_id)
    else:
        stmt = db.select(Vegetable)

    vegetables = db.session.scalars(stmt).all()
    return render_template(
        "index.html",
        vegetables=vegetables,
        category_id=category_id,
    )


@bp.route("/detail/<int:vegetable_id>")
def detail(vegetable_id):
    vegetable = db.session.scalar(
        db.select(Vegetable).where(Vegetable.id == vegetable_id)
    )
    return render_template("detail.html", vegetable=vegetable)
