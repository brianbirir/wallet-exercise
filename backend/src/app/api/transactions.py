from decimal import Decimal

from flask import abort, request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from src.app.api import user

from src.app.schema.serializer import wallet, wallet_update
from src.app.schema.validation_schema import (
    UserRequestSchema,
    WalletPutRequestSchema,
    TransferRequestSchema,
)
from src.app.db.model import (
    UserModel,
    WalletModel,
    TransactionsModel,
    CurrencyModel,
)

ns_transaction = Namespace("transaction", description="Financial transaction resource")


@ns_transaction.route("/wallet")
class Wallet(Resource):

    """Wallet resource"""

    @jwt_required()
    @ns_transaction.marshal_with(wallet)
    @ns_transaction.response(200, "Wallet details retrieved successfully")
    @ns_transaction.response(400, "Bad request")
    @ns_transaction.response(404, "Wallet does not exist")
    @ns_transaction.param("user_id", "ID of the user that the wallet belongs to")
    def get(self):
        """Get wallet"""
        schema = UserRequestSchema()
        validation_errors = schema.validate(request.args)

        if validation_errors:
            abort(400, str(validation_errors))

        user_id = request.args.get("user_id")

        if not WalletModel.find_by_user_id(user_id=user_id):
            abort(404, f"Wallet for specified user {user_id} does not exist")

        wallet, currency = WalletModel.find_by_user_id(user_id=user_id)

        return {
            "amount": wallet.amount,
            "currency": currency.currency_code,
        }, 200

    @jwt_required()
    @ns_transaction.expect(wallet_update)
    @ns_transaction.response(200, "Wallet credited successfully")
    @ns_transaction.response(400, "Bad request")
    @ns_transaction.response(404, "Wallet does not exist")
    @ns_transaction.param("user_id", "ID of the user that the wallet belongs to")
    def put(self):
        """Credits money wallet"""
        request_body = request.json

        request_param_schema = UserRequestSchema()
        request_body_schema = WalletPutRequestSchema()

        params_validation_errors = request_param_schema.validate(request.args)
        body_validation_errors = request_body_schema.validate(request_body)

        if params_validation_errors:
            abort(400, str(params_validation_errors))

        if body_validation_errors:
            abort(400, str(body_validation_errors))

        # query param
        user_id = request.args.get("user_id")

        if not WalletModel.find_by_user_id(user_id=user_id):
            abort(404, f"Wallet for specified user {user_id} does not exist")

        wallet, currency = WalletModel.find_by_user_id(user_id=user_id)

        if not wallet:
            return f"Wallet of user id {user_id} does not exist", 404

        # request body
        amount = request_body.get("amount")
        currency_id = request_body.get("currency_id")

        wallet.amount = wallet.amount + Decimal(amount)
        # wallet.currency_id = currency_id
        # wallet.user_id = user_id
        wallet.save_to_db()
        return {"message": "Wallet credited successfully"}, 200

    @jwt_required()
    @ns_transaction.expect(wallet_update)
    @ns_transaction.response(200, "Wallet successfully")
    @ns_transaction.response(400, "Bad request")
    @ns_transaction.response(404, "Wallet does not exist")
    @ns_transaction.response(406, "You have insufficient funds")
    @ns_transaction.param("user_id", "ID of the user that the wallet belongs to")
    def delete(self):
        """Debits money wallet"""
        request_body = request.json

        request_param_schema = UserRequestSchema()
        request_body_schema = WalletPutRequestSchema()

        params_validation_errors = request_param_schema.validate(request.args)
        body_validation_errors = request_body_schema.validate(request_body)

        if params_validation_errors:
            abort(400, str(params_validation_errors))

        if body_validation_errors:
            abort(400, str(body_validation_errors))

        # query param
        user_id = request.args.get("user_id")

        if not WalletModel.find_by_user_id(user_id=user_id):
            abort(404, f"Wallet for specified user {user_id} does not exist")

        wallet, currency = WalletModel.find_by_user_id(user_id=user_id)

        if not wallet:
            return f"Wallet of user id {user_id} does not exist", 404

        # request body
        amount = request_body.get("amount")
        currency_id = request_body.get("currency_id")

        if wallet.amount >= Decimal(amount):
            wallet.amount = wallet.amount - Decimal(amount)
            # wallet.currency_id = currency_id
            # wallet.user_id = user_id
            wallet.save_to_db()
            return {"message": "Wallet debited successfully"}, 200
        return {"message": "You have insufficient funds"}, 406


@ns_transaction.route("/record")
class RecordTransactions(Resource):
    pass


@ns_transaction.route("/transfer")
class TransferFunds(Resource):
    """Transfer resource"""

    @jwt_required()
    @ns_transaction.expect(wallet_update)
    @ns_transaction.response(200, "Wallet credited successfully")
    @ns_transaction.response(400, "Bad request")
    @ns_transaction.response(404, "Wallet does not exist")
    @ns_transaction.param("current_user_id", "ID of the user wants to transfer funds")
    @ns_transaction.param(
        "target_user_id", "ID of the user that receives transferred funds"
    )
    def put(self):
        """Transfer money from one user to another"""
        request_body = request.json

        request_param_schema = TransferRequestSchema()
        request_body_schema = WalletPutRequestSchema()

        params_validation_errors = request_param_schema.validate(request.args)
        body_validation_errors = request_body_schema.validate(request_body)

        if params_validation_errors:
            abort(400, str(params_validation_errors))

        if body_validation_errors:
            abort(400, str(body_validation_errors))

        # query param
        current_user_id = request.args.get("current_user_id")
        target_user_id = request.args.get("target_user_id")

        if not WalletModel.find_by_user_id(user_id=current_user_id):
            abort(
                404, f"Wallet for money transfer user {current_user_id} does not exist"
            )

        if not WalletModel.find_by_user_id(user_id=target_user_id):
            abort(
                404, f"Wallet for money receiving user {target_user_id} does not exist"
            )

        wallet_current, currency_current = WalletModel.find_by_user_id(
            user_id=current_user_id
        )

        wallet_target, currency_target = WalletModel.find_by_user_id(
            user_id=target_user_id
        )

        # request body
        amount = request_body.get("amount")
        currency_id = request_body.get("currency_id")

        if wallet_current.amount >= Decimal(amount):
            wallet_current.amount = wallet_current.amount - Decimal(amount)
            wallet_target.amount = wallet_target.amount + Decimal(amount)

            wallet_current.save_to_db()
            wallet_target.save_to_db()
            return {"message": "Money has been transferred successfully"}, 200
        return {"message": "You have insufficient funds"}, 406
