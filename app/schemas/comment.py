from marshmallow import Schema, fields, validates, ValidationError

class CommentCreateSchema(Schema):
    article_id = fields.Int(required=True)
    content = fields.Str(required=True)
    parent_id = fields.Int(allow_none=True)

    @validates("content")
    def validate_content(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Comment content cannot be empty")


class CommentUpdateSchema(Schema):
    content = fields.Str(required=True)

    @validates("content")
    def validate_content(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Comment content cannot be empty")


from marshmallow import Schema, fields
from app.schemas.user import UserResponseSchema

class CommentResponseSchema(Schema):
    id = fields.Int()
    content = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    author = fields.Nested(
        UserResponseSchema,
        attribute="user"
    )

    replies = fields.Nested(
        "CommentResponseSchema",
        many=True
    )
