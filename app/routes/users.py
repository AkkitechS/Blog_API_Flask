from app.extensions import db
from app.models.users import User
from app.schemas.user import UserSchema, UserResponseSchema
from app.utils.set_response import set_response
from flask import Blueprint, jsonify, request
from sqlalchemy import or_

users_bp = Blueprint('users', __name__)
user_schema = UserSchema()
user_response_schema = UserResponseSchema()

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return set_response(None, "Please enter all required fields", 400, False)

            error = user_schema.validate(data)
            if error:
                return set_response(None, str(error), 400, False)

            exising_user = User.query.filter(or_(User.username == data['username'], User.email == data['email'])).first()
            if exising_user:
                return set_response(None, 'User with email or username already exists', 400, False)

            user = user_schema.load(data)
            db.session.add(user)
            db.session.commit()
            return set_response(user_response_schema.dump(user), 'User registered successsfully', 200, True)

    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)