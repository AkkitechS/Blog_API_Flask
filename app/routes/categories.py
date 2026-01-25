from flask import request, Blueprint

from app.utils.set_response import set_response
from app.extensions import db
from app.models.categories import Category
from app.schemas.category import CategoryResponseSchema


category_bp = Blueprint('category', __name__)
category_response = CategoryResponseSchema(many=True)

@category_bp.route('/category-list', methods=['GET'])
def get_categories():
    try:
        if request.method == 'GET':
            categories = Category.query.all()
            print(categories)
            print(category_response.dump(categories))
            if not categories:
                return set_response(None, 'Categories not found', 404, False)
            return set_response(category_response.dump(categories), 'Categories fetched successfully', 200, True)
        else:
            return set_response(None, 'Bad Request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, 'Internal server error', 500, False)