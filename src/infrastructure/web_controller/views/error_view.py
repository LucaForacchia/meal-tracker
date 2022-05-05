from flask_restx import fields

class ErrorModel:
    def __init__(self, api):
        self.error_view = api.model("error", {
            "error_message": fields.String(required =  True)
        })

    def represent_error(self, err):
        return {
            "error_message": err
        }

