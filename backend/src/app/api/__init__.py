""" API Base"""
from flask_restx import Api

authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "Authorization Bearer"}
}

api = Api(
    title="Wallet Web API",
    version="1.0",
    description="API service to access Wallet backend app",
    doc="/docs",
    authorizations=authorizations,
)


@api.errorhandler
def default_error_handler(err):
    message = "An unhandled exception occurred: {}".format(err)
    # Flask fully logs this exception, so we don't have to
    # log.exception(message)
    return {"message": message}, 500
