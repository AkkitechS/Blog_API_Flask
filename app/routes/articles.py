from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time

from app.extensions import db
from app.models.articles import Article
from app.utils.set_response import set_response
from app.utils.slug import generate_unique_slug
from app.schemas.article import ArticleSchema, ArticleResponseSchema, ArticleUpdateSchema

articles_bp = Blueprint('articles', __name__)
article_create_schema = ArticleSchema()
article_response_schema = ArticleResponseSchema()
article_update_schema = ArticleUpdateSchema()

@articles_bp.route('/create-article', methods=['POST', 'PATCH'])
@jwt_required()
def create_article():
    try:
        article_id = request.args.get('article_id')
        user_id = get_jwt_identity()
        if request.method == 'POST':
            data = request.get_json()
            data['author_id'] = user_id
            errors = article_create_schema.validate(data)
            if errors:
                return set_response(None, errors, 400, False)

            article = article_create_schema.load(data)
            article.author_id = user_id

            db.session.add(article)
            db.session.commit()
            return set_response(article_response_schema.dump(article), 'Article created successfully', 200, True)

        elif request.method == 'PATCH' and article_id:
            print("IN UPDATE >>>>")
            print(user_id)
            print(article_id)
            data = request.get_json()
            if not data:
                return set_response(None, 'Bad Request', 400, False)

            article = Article.query.filter_by(id=article_id).first()
            if not article:
                return set_response(None, 'Article not found', 400, False)

            if article.author_id != int(user_id):
                return set_response(None, 'Unauthorized request', 401, False)

            errors = article_update_schema.validate(data, partial=True)
            if errors:
                return set_response(None, errors, 400, False)

            # ✅ Apply updates safely
            for key, value in data.items():
                setattr(article, key, value)

            db.session.commit()

            return set_response(article_response_schema.dump(article), 'Article updated successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@articles_bp.route('/get-article/public/<int:article_id>', methods=['GET'])
def get_article_public(article_id):
    try:
        if request.method == 'GET':
            if not article_id:
                return set_response(None, 'Please provide article id', 400, False)

            article = Article.query.filter(Article.id == article_id, Article.status == 'published').first()
            if not article:
                return set_response(None, 'Article not found', 404, False)
            return set_response(article_response_schema.dump(article), 'Article found successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@articles_bp.route('/get-article/private/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article_private(article_id):
    try:
        user_id = get_jwt_identity()
        if request.method == 'GET':
            if not article_id:
                return set_response(None, 'Please provide article id', 400, False)
            if not user_id:
                return set_response(None, 'Unauthorized', 401, False)

            article = Article.query.filter(Article.id == article_id, Article.author_id == user_id).first()
            if not article:
                return set_response(None, 'Article not found', 404, False)

            return set_response(article_response_schema.dump(article), 'Article found successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@articles_bp.route('/delete/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    try:
        if request.method == 'DELETE':
            if not article_id:
                return set_response(None, 'Article with given id does not exist', 400, False)

            article = Article.query.get(article_id)
            if not article or article.status == 'deleted':
                return set_response(None, 'Article not found', 400, False)

            article.status = 'deleted'
            db.session.commit()
            return set_response(None, 'Article deleted successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@articles_bp.route('/articles-list', methods=['GET'])
def get_articles_list():
    try:
        if request.method == 'GET':
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            category_id = request.args.get('category_id', type=int)
            author_id = request.args.get('author_id', type=int)
            start_date = request.args.get('start_date')  # YYYY-MM-DD
            end_date = request.args.get('end_date')  # YYYY-MM-DD

            query = Article.query

            if category_id:
                query = query.filter(Article.category_id == category_id)

            if author_id:
                query = query.filter(Article.author_id == author_id)

                # -------- Date Filters --------
            if start_date:
                start = datetime.strptime(start_date, "%d-%m-%Y")
                query = query.filter(Article.created_at >= start)

            if end_date:
                end = datetime.combine(
                    datetime.strptime(end_date, "%d-%m-%Y"),
                    time.max
                )
                query = query.filter(Article.created_at <= end)

            pagination = query.filter(Article.status=='published').order_by(Article.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

            articles = pagination.items

            schema = ArticleResponseSchema(many=True)

            response_data = {
                'articles': schema.dump(articles),
                'pagination' : {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }

            return set_response(response_data, 'Articles fetched successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@articles_bp.route('/articles-list-by-user', methods=['GET'])
@jwt_required()
def get_articles_list_by_user():
    try:
        if request.method == 'GET':
            user_id = get_jwt_identity()
            if not user_id:
                return set_response(None, 'Unauthorized request', 401, False)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status', 'published')
            category_id = request.args.get('category_id', type=int)
            start_date = request.args.get('start_date')  # YYYY-MM-DD
            end_date = request.args.get('end_date')  # YYYY-MM-DD

            query = Article.query

            if status:
                query = query.filter(Article.status == status)

            if category_id:
                query = query.filter(Article.category_id == category_id)

            # -------- Date Filters --------
            if start_date:
                start = datetime.strptime(start_date, "%d-%m-%Y")
                query = query.filter(Article.created_at >= start)

            if end_date:
                end = datetime.combine(
                    datetime.strptime(end_date, "%d-%m-%Y"),
                    time.max
                    )
                query = query.filter(Article.created_at <= end)

            pagination = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

            articles = pagination.items
            schema = ArticleResponseSchema(many=True)

            response_data = {
                'articles': schema.dump(articles),
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }

            return set_response(response_data, 'Articles fetched successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, 'Bad Request', 400, False)


@articles_bp.route('/change-status/<int:article_id>', methods=['PATCH'])
@jwt_required()
def change_article_status(article_id):
    try:
        if request.method == 'PATCH':
            data = request.get_json()
            status = data['status']
            if not data:
                return set_response(None, 'Please provide data', 400, False)

            if not status:
                return set_response(None, 'Please provide status', 400, False)

            if not article_id:
                return set_response(None, 'Please provide article id', 400, False)

            article = Article.query.get(article_id)
            if not article:
                return set_response(None, 'Article not found', 404, False)

            if article.status == 'deleted':
                return set_response(None, 'Article not found', 404, False)

            article.status = status
            db.session.commit()
            return set_response(article_response_schema.dump(article), 'Status updated successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)
