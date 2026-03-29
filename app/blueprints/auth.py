import random
import string
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, redirect, render_template, request, session  ,flash, url_for
from flask_mail import Message

from app.extensions import db, mail
from app.models import EmailCode, User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")
    remember = request.form.get("remember")

    user = db.session.scalar(db.select(User).where(User.email == email))
    if user and user.check_password(password):
        session["user_id"] = user.id
        if remember:
            session.permanent = True
        flash("登陆成功", "success")
        return redirect("/")
    else:
        flash("账号或密码错误", "error")
        return redirect(url_for("auth.login"))


@bp.post("/logout")
def logout():
    session.clear()
    return redirect("/")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")
    username = request.form.get("username")
    code = request.form.get("code")

    code_model = db.session.scalar(
        db.select(EmailCode).where(
            EmailCode.email == email,
            EmailCode.code == code,
        )
    )

    if not code_model or (datetime.now() - code_model.create_time) > timedelta(minutes=5):
        return jsonify({"result": False, "message": "验证码错误或已过期"})

    user = User(email=email, password=password, username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({"result": True})


@bp.route("/email/code")
def get_email_code():
    email = request.args.get("email")
    if not email:
        return jsonify({"result": False, "message": "请传入邮箱"})

    source = string.digits * 4
    code = "".join(random.sample(source, 4))

    message = Message(
        subject="【注册验证码】",
        recipients=[email],
        body=f"【验证码】你的验证码是：{code}",
    )

    try:
        mail.send(message)
    except Exception as e:
        return jsonify({"result": False, "message": str(e)})

    code_model = EmailCode(email=email, code=code)
    db.session.add(code_model)
    db.session.commit()

    return jsonify({"result": True, "message": "ok"})
