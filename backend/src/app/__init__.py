""" API Base"""
from flask_restx import Api


api = Api(
    title="Kachezwe web API",
    version="1.0",
    description="API service to access Kachezwe web app",
    doc="/docs",
)
