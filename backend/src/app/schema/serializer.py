from flask_restx import fields

from src.app.api import api


user = api.model(
    "UserSchema",
    {
        "user_id": fields.Integer(description="id of the user"),
        "name": fields.String(description="name of the user"),
        "email": fields.String(description="username of the user as an email address"),
        "role": fields.String(description="role of the user"),
        "telephone": fields.String(description="phone number of the user"),
        "profile_photo": fields.String(
            description="Source link for the user's profile photo"
        ),
        "last_login_date": fields.String(description="last log in datetime"),
        "is_disabled": fields.Boolean(description="is the user active or inactive"),
    },
)

role = api.model(
    "RoleSchema",
    {
        "role_id": fields.Integer(description="ID of the role"),
        "role_name": fields.String(description="name of the role"),
    },
)

role_post_request = api.model(
    "RolePostRequestSchema",
    {
        "role_name": fields.String(description="Name of the role"),
    },
)

user_get_request = api.model(
    "GetUserRequestSchema", {"user_id": fields.String(description="ID of the user")}
)

user_registration_request = api.model(
    "UserRegistrationRequestSchema",
    {
        "name": fields.String(description="Name of the user"),
        "email": fields.String(description="Email address of the user"),
        "password": fields.String(description="Password"),
        "profile_photo": fields.String(
            description="Source link for the user's profile photo"
        ),
        "telephone": fields.String(description="Telephone number of the user"),
        "role_id": fields.Integer(description="Role id of the user"),
    },
)

user_post_request = api.model(
    "PostUserRequestSchema",
    {
        "name": fields.String(description="Name of the user"),
        "email": fields.String(description="username of the user as an email address"),
        "password": fields.String(description="Password"),
        "profile_photo": fields.String(
            description="Source link for the user's profile photo"
        ),
        "telephone": fields.String(description="Telephone number of the user"),
        "role_id": fields.Integer(description="Role id of the user"),
        "is_disabled": fields.Boolean(description="user active state"),
    },
)

user_login_request = api.model(
    "UserLoginRequestSchema",
    {
        "email": fields.String(description="Email address of the user"),
        "password": fields.String(description="Password"),
    },
)

wallet = api.model(
    "WalletSchema",
    {
        "amount": fields.Float(description="Amount in the wallet"),
        "currency": fields.String(description="Current currency"),
    },
)
