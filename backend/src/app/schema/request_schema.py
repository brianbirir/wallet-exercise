""" Schema for parsing & validating request data"""
from marshmallow import Schema, fields


class UserRequestSchema(Schema):
    user_id = fields.Number(required=True)


class UserRegistrationRequestSchema(Schema):
    username = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password = fields.String(required=True)
    telephone = fields.String(required=True)
    gender = fields.String(required=True)
    role_id = fields.Number(required=True)


class UserPutRequestSchema(Schema):
    username = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    password = fields.String(required=True)
    telephone = fields.String(required=True)
    role_id = fields.Number(required=True)
    is_disabled = fields.Boolean(required=True)


class UserLoginRequestSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class RoleParamRequestSchema(Schema):
    role_id = fields.Number(required=True)


class RolePostRequestSchema(Schema):
    role_name = fields.String(required=True)


class RolePutRequestSchema(Schema):
    role_name = fields.String(required=True)


class AthleteVerificationRequestSchema(Schema):
    is_verified = fields.Boolean(required=True)
