from flask import Blueprint, render_template, request ,abort

from app.extensions import db
from app.models import Vegetable

bp = Blueprint("main", __name__)


from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Vegetable, VegetableCategory

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "", type=str).strip()
    category_id = request.args.get("category_id", type=int)

    stmt = db.select(Vegetable).order_by(Vegetable.id.desc())

    # 关键词搜索
    if q:
        stmt = stmt.where(
            or_(
                Vegetable.name.contains(q),
                Vegetable.place.contains(q)
            )
        )

    # 分类筛选
    if category_id:
        stmt = stmt.where(Vegetable.category_id == category_id)

    pagination = db.paginate(stmt, page=page, per_page=2, error_out=False)
    vegetables = pagination.items

    return render_template(
        "index.html",
        vegetables=vegetables,
        pagination=pagination,
        q=q,
        category_id=category_id,
    )

@bp.route("/detail/<int:vegetable_id>")
def detail(vegetable_id):
    vegetable = db.session.scalar(
        db.select(Vegetable).where(Vegetable.id == vegetable_id)
    )
    if(vegetable is None):
        abort(404);
    return render_template("detail.html", vegetable=vegetable)
