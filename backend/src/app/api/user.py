from datetime import datetime

from flask import abort, request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required

from src.utils import pagination
from src.app.db.model import UserModel, RolesModel
from src.app.schema.serializer import user_post_request, user
from src.app.schema.request_schema import (
    UserRequestSchema,
    UserRegistrationRequestSchema,
    UserPutRequestSchema,
)

ns_user = Namespace("user", description="User resource")


@ns_user.route("")
class User(Resource):
    """The user resource"""

    @jwt_required
    @ns_user.marshal_with(user)
    @ns_user.response(200, "User details returned successfully")
    @ns_user.response(400, "Bad request")
    @ns_user.response(404, "User not found")
    @ns_user.param("user_id", "ID of the user")
    def get(self):
        """Get user"""
        schema = UserRequestSchema()
        validation_errors = schema.validate(request.args)

        if validation_errors:
            abort(400, str(validation_errors))

        user_id = request.args.get("user_id")
        user = UserModel.find_by_user_id(user_id)

        if user:
            role_object = RolesModel().find_by_role_id(user.role_id)
            return {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "telephone": user.telephone,
                "profile_photo": user.profile_photo,
                "last_login_date": user.last_login_date,
                "role": role_object.name,
                "is_disabled": user.is_disabled,
            }, 200
        else:
            abort(404, "User does not exist")

    @jwt_required
    @ns_user.expect(user_post_request)
    @ns_user.response(200, "User was added successfully")
    @ns_user.response(400, "Bad request")
    @ns_user.response(409, "User already exists")
    def post(self):
        """Adds new user"""
        request_body = request.json
        schema = UserRegistrationRequestSchema()
        validation_errors = schema.validate(request_body)

        if validation_errors:
            abort(400, str(validation_errors))

        password = request_body.get("password")
        name = request_body.get("name")
        email = request_body.get("email")
        telephone = request_body.get("telephone")
        profile_photo = request_body.get("profile_photo")
        role_id = request_body.get("role_id")

        if UserModel.find_by_username(email):
            return {"message": f"User {email} already exists"}, 409

        # create new user
        new_user = UserModel(
            password=UserModel.generate_hash(password),
            name=name,
            email=email,
            telephone=telephone,
            profile_photo=profile_photo,
            is_disabled=False,
            role_id=role_id,
        )

        try:
            new_user.save_to_db()
            return {
                "message": f"User {email} was created successfully",
            }, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500

    @jwt_required
    @ns_user.expect(user_post_request)
    @ns_user.param("user_id", "ID of the user")
    @ns_user.response(200, "User updated successfully")
    @ns_user.response(400, "Bad request")
    @ns_user.response(404, "User does not exist")
    def put(self):
        """Updates user"""
        request_body = request.json
        request_body_schema = UserPutRequestSchema()
        request_param_schema = UserRequestSchema()
        body_validation_errors = request_body_schema.validate(request_body)
        args_validation_error = request_param_schema.validate(request.args)

        if body_validation_errors:
            abort(400, str(body_validation_errors))

        if args_validation_error:
            abort(400, str(args_validation_error))

        # request body
        email = request_body.get("email")
        password = request_body.get("password")
        name = request_body.get("name")
        telephone = request_body.get("telephone")
        profile_photo = request_body.get("profile_photo")
        role_id = request_body.get("role_id")
        is_disabled = request_body.get("is_disabled")

        # query param
        user_id = request.args.get("user_id")

        user = UserModel.find_by_user_id(user_id)
        if not user:
            return {"message": f"User of id {user_id} does not exist"}, 404

        try:
            if user:
                user.name = name
                user.email = email
                user.profile_photo = profile_photo
                user.telephone = telephone
                user.password = UserModel.generate_hash(password)
                user.updated_at = datetime.utcnow()
                user.role_id = role_id
                user.is_disabled = is_disabled
                user.save_to_db()
                return {"message": f"User {email} has been updated successfully"}, 200
            else:
                abort(404, "User not found")
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500

    @jwt_required
    @ns_user.response(200, "User deleted successfully")
    @ns_user.response(400, "Bad request")
    @ns_user.response(404, "User not found")
    @ns_user.param("user_id", "ID of the user")
    def delete(self):
        """Deletes user"""
        schema = UserRequestSchema()
        validation_errors = schema.validate(request.args)

        if validation_errors:
            abort(400, str(validation_errors))

        user_id = request.args.get("user_id")

        try:
            user = UserModel.find_by_user_id(user_id)
            if user:
                user.delete_from_db()
                return {"message": f"User has been deleted"}, 200
            else:
                abort(404, "User not found")
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500


@ns_user.route("/all")
class Users(Resource):
    """The users resource"""

    @jwt_required
    @ns_user.marshal_with(user, as_list=True)
    @ns_user.response(200, "Users returned successfully")
    @ns_user.response(400, "Bad request")
    @ns_user.response(404, "Users not found")
    @ns_user.param("page", "Page number")
    @ns_user.param("limit", "Number of users per page")
    def get(self):
        """Gets all users"""
        page = request.args.get("page")
        limit = request.args.get("limit")

        user = UserModel.get_all_paginated_users(
            page=pagination.default_page_value(page),
            per_page=pagination.default_limit_value(limit),
        )

        user_items = user.items

        if user_items:
            new_users = []

            # data transformation
            for user_object in user_items:
                new_user_object = dict()
                role_object = RolesModel().find_by_role_id(user_object.role_id)
                new_user_object["user_id"] = user_object.id
                new_user_object["name"] = user_object.name
                new_user_object["email"] = user_object.email
                new_user_object["telephone"] = user_object.telephone
                new_user_object["profile_photo"] = user_object.profile_photo
                new_user_object["role"] = role_object.name
                new_user_object["is_disabled"] = user_object.is_disabled
                new_users.append(new_user_object)
            return new_users, 200
        else:
            abort(404, "No users found")
