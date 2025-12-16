from flask import Blueprint, request
from flask_jwt_extended import  create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from sqlalchemy import or_

from app.extensions import db
from app.utils.set_response import set_response
from app.schemas.login import LoginSchema
from app.schemas.user import UserResponseSchema
from app.models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity


auth_bp = Blueprint('auth', __name__)
user_response_schema = UserResponseSchema()
user_login_schema = LoginSchema()

def create_access_refresh_tokens(identity, payload):
    try:
        access_token = create_access_token(identity=identity, additional_claims=payload)
        refresh_token = create_refresh_token(identity=identity)
        return {'access_token': access_token, 'refresh_token': refresh_token}
    except Exception as e:
        raise e


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return set_response(None, 'Invalid data', 400, False)

            error = user_login_schema.validate(data)
            if error:
                return set_response(None, str(error), 400, False)

            user = User.query.filter(or_(User.email == data['identity'], User.username == data['identity'])).first()
            if not user:
                return set_response(None, 'User does not exist', 400, False)

            if not check_password_hash(user.password, data['password']):
                return set_response(None, 'Invalid credentials', 401, False)

            tokens = create_access_refresh_tokens(user.id, user_response_schema.dump(user))
            response = {
                'user': user_response_schema.dump(user),
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token']
            }
            return set_response(response, "Login successful", 200, True)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)

@auth_bp.route('/refresh',methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_id)
        return set_response(new_access_token, "Refresh successful", 200, True)
    except Exception as e:
        return set_response(None, str(e), 401, False)