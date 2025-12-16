from marshmallow import fields, Schema

class LoginSchema(Schema):
    identity = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)