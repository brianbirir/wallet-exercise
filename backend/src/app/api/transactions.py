from flask import abort, request
from flask_restx import Namespace, Resource

from src.app.schema.serializer import user_login_request, user_registration_request
from src.app.schema.request_schema import (
    UserRegistrationRequestSchema,
    UserLoginRequestSchema,
)
from src.app.db.model import (
    UserModel,
    WalletModel,
    TransactionsModel,
    CurrencyModel,
)

ns_transaction = Namespace("transaction", description="Financial transaction resource")


@ns_transaction.route("/wallet")
class Wallet:
    pass


@ns_transaction.route("/credit")
class CreditAccount:
    pass


@ns_transaction.route("/debit")
class DebitAccount:
    pass


@ns_transaction.route("/record")
class RecordTransactions:
    pass


@ns_transaction.route("/transfer")
class TransferFunds:
    pass
