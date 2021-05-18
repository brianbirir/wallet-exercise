from flask_restx import Namespace, Resource

ns_healthz = Namespace("healthz", description="Tests health of the RESTful API service")


@ns_healthz.route("/status")
class Healthz(Resource):
    """Healthz checks if API service is running"""

    @ns_healthz.response(200, "API service is up and running")
    def get(self):
        return {"message": "API service is up and running"}, 200
