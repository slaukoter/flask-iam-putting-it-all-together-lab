from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", back_populates="user")

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.generate_password_hash(password_bytes)
        self._password_hash = hashed.decode("utf-8")

    def authenticate(self, password):
        password_bytes = password.encode("utf-8")
        return bcrypt.check_password_hash(
            self._password_hash.encode("utf-8"),
            password_bytes
        )

    @validates("username")
    def validate_username(self, key, value):
        if not value:
            raise ValueError("Username must be present.")
        return value


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="recipes")

    @validates("title")
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title must be present.")
        return value

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters.")
        return value


class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
    image_url = fields.String()
    bio = fields.String()


class RecipeSchema(Schema):
    id = fields.Int()
    title = fields.String()
    instructions = fields.String()
    minutes_to_complete = fields.Int()
    user = fields.Nested(UserSchema)
