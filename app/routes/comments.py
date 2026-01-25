from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time

from app.extensions import db
from app.models.comments import Comment
from app.models.articles import Article
from app.utils.set_response import set_response
from app.utils.slug import generate_unique_slug
from app.schemas.comment import CommentCreateSchema, CommentUpdateSchema, CommentResponseSchema


comments_bp = Blueprint('comments', __name__)
comments_create_schema = CommentCreateSchema()
comments_update_schema = CommentUpdateSchema()
comments_response_schema = CommentResponseSchema()
comments_response_schema_many = CommentResponseSchema(many=True)

@comments_bp.route('/create-comment', methods=['POST', 'PATCH'])
@jwt_required()
def create_comment():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return set_response(None, 'Invalid data', 400, False)

            errors = comments_create_schema.validate(data)
            if errors:
                return set_response(None, errors, 400, False)

            comment = comments_create_schema.load(data)
            user_id = get_jwt_identity()

            if not user_id:
                return set_response(None, 'User does not exist', 404, False)

            article = Article.query.filter_by(id=comment.get('article_id'), status='published').first()
            if not article:
                return set_response(None, 'Article does not exist', 404, False)

            if comment.get('parent_id'):
                parent = Comment.query.filter_by(id=comment.get('parent_id'), article_id=comment.get('article_id')).first()
                if not parent:
                    return set_response(None, 'Parent comment not found', 404, False)

            created_comment = Comment(content=comment.get('content'), article_id=comment.get('article_id'), author_id=user_id, parent_id=comment.get('parent_id'))
            db.session.add(created_comment)
            db.session.commit()
            return set_response(comments_response_schema.dump(created_comment), 'Comment posted successfully', 200, True)

        elif request.method == 'PATCH':
            data = comments_update_schema.load(request.get_json())
            comment_id = request.args.get('comment_id')
            if not data:
                return set_response(None, 'Invalid data', 400, False)

            errors = comments_update_schema.validate(data)
            if errors:
                return set_response(None, errors, 400, False)

            user_id = get_jwt_identity()

            if not user_id:
                return set_response(None, 'User does not exist', 404, False)

            comment = Comment.query.get(comment_id)
            if not comment:
                return set_response(None, 'Comment does not exist', 404, False)

            comment.content = data.get('content')
            db.session.commit()
            return set_response(comments_response_schema.dump(comment), 'Comment updated successfully', 200, True)
        else:
            return set_response(None, 'Bad request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@comments_bp.route('/delete-comment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        if request.method == 'DELETE':
            if not comment_id:
                return set_response(None, 'Invalid data', 400, False)

            comment = Comment.query.get(comment_id)
            if not comment:
                return set_response(None, 'Comment does not exist', 404, False)

            db.session.delete(comment)
            db.session.commit()
            return set_response(None, 'Comment deleted successfully', 200, True)
        else:
            return set_response(None, 'Bad request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@comments_bp.route('/comments-list', methods=['GET'])
def get_comments_list():
    try:
        if request.method == 'GET':
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            article_id = request.args.get('article_id')

            if not article_id:
                return set_response(None, 'Invalid data', 400, False)

            article = Article.query.filter_by(id=article_id, status='published').first()
            if not article:
                return set_response(None, 'Article does not exist', 404, False)

            query = Comment.query.filter_by(article_id=article_id)
            pagination = query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            comments = pagination.items

            response = {
                'comments': comments_response_schema_many.dump(comments),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            return set_response(response, 'Comments fetched successfully', 200, True)
        else:
            return set_response(None, 'Bad request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)