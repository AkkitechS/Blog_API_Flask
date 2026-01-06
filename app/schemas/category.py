from marshmallow import Schema, fields, post_load


class CategoryResponseSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer()
    name = fields.String()
    slug = fields.String()
    description = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()