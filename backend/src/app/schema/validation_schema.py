""" Schema for parsing & validating request data"""
from re import L
from marshmallow import Schema, fields


class UserRequestSchema(Schema):
    user_id = fields.Number(required=True)


class UserRegistrationRequestSchema(Schema):
    email = fields.String(required=True)
    name = fields.String(required=True)
    password = fields.String(required=True)
    telephone = fields.String(required=True)
    profile_photo = fields.String(required=True)
    role_id = fields.Number(required=True)
    is_disabled = fields.Boolean(required=True)


class UserPutRequestSchema(Schema):
    email = fields.String(required=True)
    name = fields.String(required=True)
    profile_photo = fields.String(required=True)
    password = fields.String(required=True)
    telephone = fields.String(required=True)
    role_id = fields.Number(required=True)
    is_disabled = fields.Boolean(required=True)


class UserLoginRequestSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class RoleParamRequestSchema(Schema):
    role_id = fields.Number(required=True)


class RolePostRequestSchema(Schema):
    role_name = fields.String(required=True)


class RolePutRequestSchema(Schema):
    role_name = fields.String(required=True)


class AthleteVerificationRequestSchema(Schema):
    is_verified = fields.Boolean(required=True)


class WalletPutRequestSchema(Schema):
    amount = fields.Float(required=True)
    currency_id = fields.Integer(required=False)


class TransferRequestSchema(Schema):
    current_user_id = fields.Integer(required=True)
    target_user_id = fields.Integer(required=True)
