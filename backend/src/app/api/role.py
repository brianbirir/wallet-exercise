from datetime import datetime

from flask import abort, request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required

from src.utils import pagination
from src.app.db.model import RolesModel
from src.app.schema.serializer import role_post_request, role
from src.app.schema.validation_schema import (
    RoleParamRequestSchema,
    RolePostRequestSchema,
    RolePutRequestSchema,
)

ns_role = Namespace("role", description="Role resource")


@ns_role.route("")
class Role(Resource):
    """The role resource"""

    @jwt_required
    @ns_role.marshal_with(role)
    @ns_role.response(200, "Role details returned successfully")
    @ns_role.response(400, "Bad request")
    @ns_role.response(404, "Role not found")
    @ns_role.param("role_id", "ID of the role")
    def get(self):
        """Get role"""
        schema = RoleParamRequestSchema()
        validation_errors = schema.validate(request.args)

        if validation_errors:
            abort(400, str(validation_errors))

        role_id = request.args.get("role_id")
        role = RolesModel.find_by_role_id(role_id)

        if role:
            return {"role_id": role.entity_id, "role_name": role.name}, 200
        else:
            abort(404, "Role does not exist")

    @jwt_required
    @ns_role.expect(role_post_request)
    @ns_role.response(200, "Role was added successfully")
    @ns_role.response(400, "Bad request")
    @ns_role.response(409, "Role already exists")
    def post(self):
        """Create new role"""
        request_body = request.json
        schema = RolePostRequestSchema()
        validation_errors = schema.validate(request_body)

        if validation_errors:
            abort(400, str(validation_errors))

        role_name = request_body.get("role_name")

        if RolesModel.find_by_name(role_name):
            return {"message": f"{role_name} role already exists"}, 409

        new_role = RolesModel(name=role_name)

        try:
            new_role.save_to_db()
            return {
                "message": f"{role_name} role was created successfully",
            }, 200
        except Exception as e:
            return {"message": f"something went wrong: {str(e)}"}, 500

    @jwt_required
    @ns_role.expect(role_post_request)
    @ns_role.param("role_id", "ID of the role")
    @ns_role.response(200, "Role updated successfully")
    @ns_role.response(400, "Bad request")
    @ns_role.response(404, "Role does not exist")
    def put(self):
        """Update role"""
        request_body = request.json
        request_body_schema = RolePutRequestSchema()
        request_param_schema = RoleParamRequestSchema()
        body_validation_errors = request_body_schema.validate(request_body)
        args_validation_error = request_param_schema.validate(request.args)

        if body_validation_errors:
            abort(400, str(body_validation_errors))

        if args_validation_error:
            abort(400, str(args_validation_error))

        # request body
        role_name = request_body.get("role_name")

        # query param
        role_id = request.args.get("role_id")

        role = RolesModel.find_by_role_id(role_id)

        if role:
            role.name = role_name
            role.save_to_db()
            return {"message": f"{role_name} role has been updated successfully"}, 200
        else:
            abort(404, "Role not found")

    @jwt_required
    @ns_role.response(200, "Role deleted successfully")
    @ns_role.response(400, "Bad request")
    @ns_role.response(404, "Role not found")
    @ns_role.param("role_id", "ID of the role")
    def delete(self):
        """Delete role"""
        schema = RoleParamRequestSchema()
        validation_errors = schema.validate(request.args)

        if validation_errors:
            abort(400, str(validation_errors))

        role_id = request.args.get("role_id")
        role = RolesModel.find_by_role_id(role_id)

        if role:
            role.delete_from_db()
            return {"message": f"Role {role.name} has been deleted successfully"}, 200
        else:
            abort(404, "Role not found")


@ns_role.route("/all")
class Users(Resource):
    """Roles resource"""

    @jwt_required
    @ns_role.marshal_with(role, as_list=True)
    @ns_role.response(200, "Roles returned successfully")
    @ns_role.response(400, "Bad request")
    @ns_role.response(404, "Roles not found")
    @ns_role.param("page", "Page number")
    @ns_role.param("limit", "Number of roles per page")
    def get(self):
        """Gets all roles"""
        page = request.args.get("page")
        limit = request.args.get("limit")

        role = RolesModel.get_all_paginated_roles(
            page=pagination.default_page_value(page),
            per_page=pagination.default_limit_value(limit),
        )

        role_items = role.items

        if role_items:
            new_role = []
            for role_object in role_items:
                new_role_object = dict()
                new_role_object["role_id"] = role_object.id
                new_role_object["role_name"] = role_object.name
                new_role.append(new_role_object)
            return new_role, 200
        else:
            abort(404, "No roles found")
