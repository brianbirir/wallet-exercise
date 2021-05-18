from datetime import datetime

from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column

from src.extensions import db


class BaseModel(db.Model):
    """Generates basic columns and contains base functions for all models

    Args:
        db.Model (class): A declarative base for declaring models.

    """

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def save_to_db(self):
        """Writes data to the database"""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Deletes data  from the database"""
        db.session.delete(self)
        db.session.commit()


class RolesModel(BaseModel):
    """Generates roles table"""

    __tablename__ = "Roles"
    name = db.Column(db.String(128), nullable=False)
    users = db.relationship("UserModel", backref="roles", lazy=True)

    def __repr__(self):
        return "<name: {} >".format(self.name)

    @classmethod
    def check_for_roles(cls):
        """Checks if roles are available"""
        return cls.query.first()

    @classmethod
    def find_by_role_id(cls, role_id):
        """Returns user by role id"""
        return cls.query.filter_by(entity_id=role_id).first()

    @classmethod
    def find_by_name(cls, role_name):
        """Returns by role name"""
        return cls.query.filter_by(name=role_name).first()

    @classmethod
    def get_all_roles(cls):
        """Returns all roles"""
        return cls.query.all()

    @classmethod
    def get_all_paginated_roles(cls, page=1, per_page=10):
        """Returns all roles by page and limit"""
        query = cls.query.order_by(cls.created_at.desc()).paginate(
            page=int(page), per_page=int(per_page), error_out=True
        )
        return query


class UserModel(BaseModel):
    """Generates user table"""

    __tablename__ = "Users"
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    telephone = db.Column(db.String(40), nullable=True)
    password = db.Column(db.String(40), nullable=False)
    profile_photo = db.Column(db.String(128), nullable=True)
    is_disabled = db.Column(db.Boolean, nullable=False, default=False)
    last_login_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())
    role_id = db.Column(db.Integer, db.ForeignKey("Roles.id"), nullable=False)

    def __repr__(self):
        return "<name: {} >".format(self.name)

    @classmethod
    def find_by_username(cls, user):
        """Returns by username"""
        return cls.query.filter_by(email=user).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        """Returns user by user id"""
        return cls.query.filter_by(id=user_id).first()

    @staticmethod
    def generate_hash(password):
        """Generates a password hash from raw password"""
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password, password_hash):
        """Verifies provided password against hashed password"""
        return pbkdf2_sha256.verify(password, password_hash)

    @classmethod
    def get_all_users(cls):
        """Returns all users"""
        return cls.query.all()


class RevokedTokenModel(BaseModel):
    """Generates revoked token table"""

    __tablename__ = "RevokedToken"
    revoked_token = db.Column(db.String(120))

    def __repr__(self):
        return "<id: revoked_token: {} >".format(self.revoked_token)

    @classmethod
    def is_token_blacklisted(cls, token):
        query = cls.query.filter_by(revoked_token=str(token)).first()
        return bool(query)
