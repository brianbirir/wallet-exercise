from flask import abort, request
from flask_restx import Namespace, Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from src.app.schema.serializer import user_login_request, user_registration_request
from src.app.schema.request_schema import (
    UserRegistrationRequestSchema,
    UserLoginRequestSchema,
)
from src.app.db.model import UserModel, RevokedTokenModel, RolesModel

ns_auth = Namespace("auth", description="Authentication resource")


@ns_auth.route("/register-user")
class UserRegistration(Resource):
    """user registration"""

    @ns_auth.expect(user_registration_request)
    @ns_auth.response(200, "User registered successfully")
    @ns_auth.response(400, "Bad request")
    @ns_auth.response(403, "User already exists")
    def post(self):
        request_body = request.json
        schema = UserRegistrationRequestSchema()
        validation_errors = schema.validate(request_body)

        if validation_errors:
            abort(400, str(validation_errors))

        username = request_body.get("username")
        password = request_body.get("password")
        first_name = request_body.get("first_name")
        last_name = request_body.get("last_name")
        telephone = request_body.get("telephone")
        role_id = request_body.get("role_id")
        gender = request_body.get("gender")

        if UserModel.find_by_username(username):
            return {"message": f"User {username} already exists"}, 409

        # create new user
        new_user = UserModel(
            email=username,
            password=UserModel.generate_hash(password),
            first_name=first_name,
            last_name=last_name,
            telephone=telephone,
            is_disabled=False,  # user is not disabled on initial registration
            role_id=role_id,
            gender=gender,
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {
                "message": f"User {username} was created",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": new_user.entity_id,
            }, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500


@ns_auth.route("/login")
class UserLogin(Resource):
    """Login resource for user"""

    @ns_auth.expect(user_login_request)
    @ns_auth.response(200, "User logged in successfully")
    @ns_auth.response(400, "Bad request")
    @ns_auth.response(404, "User does not exist")
    @ns_auth.response(401, "Wrong credentials")
    def post(self):
        request_body = request.json
        schema = UserLoginRequestSchema()
        validation_errors = schema.validate(request_body)

        if validation_errors:
            abort(400, str(validation_errors))

        user = request_body["username"]
        password = request_body["password"]

        # search by user by username
        current_user = UserModel.find_by_username(user)

        if not current_user:
            return {"message": f"User {user} does not exist!"}, 404

        # compare request password and hash
        if UserModel.verify_hash(password, current_user.password):
            # get role object
            role_object = RolesModel().find_by_role_id(current_user.role_id)
            access_token = create_access_token(identity=user, expires_delta=False)
            refresh_token = create_refresh_token(identity=user)
            return {
                "message": f"Logged in as {current_user.first_name} {current_user.last_name}",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "name": f"{current_user.first_name} {current_user.last_name}",
                "username": f"{current_user.email}",
                "user_id": f"{current_user.entity_id}",
                "role_name": role_object.name,
            }, 200
        else:
            return {"message": "Wrong credentials"}, 401


@ns_auth.route("/logout")
class UserLogoutAccess(Resource):
    """User logout to revoke access token"""

    @jwt_required
    @ns_auth.response(200, "Access token has been revoked")
    @ns_auth.response(500, "Something went wrong")
    @ns_auth.response(400, "No JWT provided")
    def delete(self):
        jti = get_jwt()["jti"]
        if not jti:
            abort(400, "No JWT provided")
        try:
            revoked_token = RevokedTokenModel(revoked_token=jti)
            revoked_token.save_to_db()
            return {"message": "Access token has been revoked"}, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500


@ns_auth.route("/logout/refresh")
class UserLogoutRefresh(Resource):
    """User logout to revoke refresh token"""

    @jwt_required(refresh=True)
    @ns_auth.doc(security="apikey")
    @ns_auth.response(200, "Refresh token has been revoked")
    @ns_auth.response(500, "Something went wrong")
    @ns_auth.response(400, "No JWT provided")
    def delete(self):
        jti = get_jwt()["jti"]

        if not jti:
            abort(400, "No JWT provided")

        try:
            revoked_token = RevokedTokenModel(revoked_token=jti)
            revoked_token.save_to_db()
            return {"message": "Refresh token has been revoked"}, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500


@ns_auth.route("/refresh")
class TokenRefresh(Resource):
    """Refreshes token

    a blacklisted refresh token will not be able to access this endpoint
    """

    @jwt_required(refresh=True)
    @ns_auth.response(200, "Access token has been generated successfully after refresh")
    @ns_auth.response(500, "Something went wrong")
    @ns_auth.response(400, "No JWT identity provided")
    def post(self):
        current_user = get_jwt_identity()

        if not current_user:
            abort(400, "No JWT identity provided")

        try:
            return {
                "message": "Refresh token has been generated successfully",
                "access_token": create_access_token(identity=current_user),
            }, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500
