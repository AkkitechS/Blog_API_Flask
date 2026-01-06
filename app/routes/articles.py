from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

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
        article_id = int(request.args.get('article_id'))
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



@articles_bp.route('/delete/<int:article_id>')
@jwt_required()
def delete_article(article_id):
    pass
