from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    _password: Mapped[str] = mapped_column(String(300))

    vegetables: Mapped[list["Vegetable"]] = relationship(
        "Vegetable", back_populates="publisher"
    )

    def __init__(self, *args, **kwargs):
        self.email = kwargs.get("email")
        password = kwargs.pop("password", None)
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class VegetableCategory(db.Model):
    __tablename__ = "vegetable_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    vegetables: Mapped[list["Vegetable"]] = relationship(
        "Vegetable", back_populates="category"
    )


class Vegetable(db.Model):
    __tablename__ = "vegetable"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    content: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    picture: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(20))
    place: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(100))
    pub_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vegetable_category.id")
    )
    category: Mapped["VegetableCategory"] = relationship(
        "VegetableCategory", back_populates="vegetables"
    )

    publisher_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    publisher: Mapped["User"] = relationship("User", back_populates="vegetables")


class EmailCode(db.Model):
    __tablename__ = "email_code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(255))
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class PredictionRecord(db.Model):
    __tablename__ = "prediction_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_category_name = db.Column(db.String(50), nullable=True)
    latency_ms = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="success")
    error_message = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("prediction_records", lazy="dynamic"))
