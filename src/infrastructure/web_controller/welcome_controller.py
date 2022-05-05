from flask_restx import Namespace, Resource, fields

from .views.version_view import VersionModel

api = Namespace("welcome",
                description="Service welcome")

version_model = VersionModel(api)

@api.route('/')
class WelcomeMessage(Resource):
    @api.doc('welcome')
    @api.marshal_with(version_model.software_version_view)
    def get(self):
        return (version_model.represent_software_status(), 200)

