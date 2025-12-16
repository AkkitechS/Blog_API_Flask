from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError, post_load, Schema
from app.models.users import User
from app.extensions import db
from werkzeug.security import generate_password_hash
import re

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        include_fk = True
        ordered = True

    id = fields.Int()
    name = fields.String(required=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    avatar = fields.String(allow_none=True)
    status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    articles = fields.List(fields.Dict())
    comments = fields.List(fields.Dict())

    @validates('username')
    def validate_username(self, value, **kwargs):
        if len(value) < 3:
            raise ValidationError('Username must be at least 3 characters long')

    @validates('password')
    def validate_password(self, value, **kwargs):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'

        if not bool(re.match(pattern, value)):
            raise ValidationError("Password must be 12+ characters long and must include upper and lower case alphabets, numbers, symbols")

    @post_load
    def hash_password(self, data, **kwargs):
        if 'password' in data:
            data['password'] = generate_password_hash(data['password'])
        return data

    @post_load
    def data_to_lower_case(self, data, **kwargs):
        if 'username' in data:
            data['username'] = data['username'].lower()
        return data


class UserResponseSchema(Schema):

    class Meta:
        ordered = True

    id = fields.Int()
    name = fields.String(required=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    avatar = fields.String(allow_none=True)
    status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)