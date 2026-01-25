from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema
from marshmallow import fields, validates, ValidationError, Schema, pre_load, validate
from app.models.articles import Article
from app.extensions import db
from app.schemas.user import UserResponseSchema
from app.schemas.category import CategoryResponseSchema
from app.utils.slug import generate_unique_slug
from werkzeug.security import generate_password_hash
import re


class ArticleSchema(SQLAlchemySchema):
    class Meta:
        model = Article
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        include_fk = True
        ordered = True

    id = fields.Int()
    title = fields.String(required=True)
    content = fields.String(required=True)
    slug = fields.String(required=True)
    status = fields.String(validate=validate.OneOf(["draft", "published"]))
    author_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('title')
    def validate_title(self, value, **kwargs):
        if len(value.strip()) < 5:
            raise ValidationError("Title must be at least 5 characters long")

    @validates("content")
    def validate_content(self, value, **kwargs):
        if len(value.strip()) < 20:
            raise ValidationError("Content must be at least 20 characters long")

    @pre_load()
    def generate_slug(self, data, **kwargs):
        if 'title' in data:
            data['slug'] = generate_unique_slug(data['title'])
        return data

class ArticleResponseSchema(Schema):
    id = fields.Int()
    title = fields.String(required=True)
    content = fields.String(required=True)
    slug = fields.String(required=True)
    status = fields.String(dump_only=True)
    author = fields.Nested('UserResponseSchema', only=('id', 'name', 'email', 'username', 'avatar'))
    category = fields.Nested('CategoryResponseSchema', only=('id', 'name', 'slug', 'description'))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ArticleUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Article
        load_instance = False
        sqla_session = db.session
        include_fk = True
        ordered = True
        partial = True   # ⭐ KEY POINT

    title = fields.String()
    content = fields.String()
    category_id = fields.Int()

    @validates("title")
    def validate_title(self, value, **kwargs):
        if len(value.strip()) < 5:
            raise ValidationError("Title must be at least 5 characters long")

    @validates("content")
    def validate_content(self, value, **kwargs):
        if len(value.strip()) < 20:
            raise ValidationError("Content must be at least 20 characters long")