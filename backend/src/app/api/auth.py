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

        email = request_body.get("email")
        password = request_body.get("password")
        name = request_body.get("name")
        telephone = request_body.get("telephone")
        role_id = request_body.get("role_id")
        profile_photo = request_body.get("profile_photo")

        if UserModel.find_by_username(email):
            return {"message": f"User {email} already exists"}, 409

        # create new user
        new_user = UserModel(
            email=email,
            password=UserModel.generate_hash(password),
            name=name,
            telephone=telephone,
            profile_photo=profile_photo,
            is_disabled=False,  # user is not disabled on initial registration
            role_id=role_id,
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            return {
                "message": f"User {email} was created",
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

        email = request_body["email"]
        password = request_body["password"]

        # search by user by username
        current_user = UserModel.find_by_username(email)

        if not current_user:
            return {"message": f"User {email} does not exist!"}, 404

        # compare request password and hash
        if UserModel.verify_hash(password, current_user.password):
            # get role object
            role_object = RolesModel().find_by_role_id(current_user.role_id)
            access_token = create_access_token(identity=email, expires_delta=False)
            refresh_token = create_refresh_token(identity=email)
            return {
                "message": f"Logged in as {current_user.name}",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "name": f"{current_user.name}",
                "email": f"{current_user.email}",
                "user_id": f"{current_user.id}",
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
