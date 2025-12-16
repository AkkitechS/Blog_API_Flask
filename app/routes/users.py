from app.extensions import db
from app.models.users import User
from app.schemas.user import UserSchema, UserResponseSchema
from app.utils.set_response import set_response
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.upload_to_cloudinary import upload_to_cloudinary


users_bp = Blueprint('users', __name__)
user_schema = UserSchema()
user_response_schema = UserResponseSchema()

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            data = request.form.to_dict()
            avatar_file = request.files.get('avatar')
            print(data)
            print(request.files)
            if not data:
                return set_response(None, "Please enter all required fields", 400, False)

            error = user_schema.validate(data)
            print(error)
            if error:
                return set_response(None, str(error), 400, False)

            exising_user = User.query.filter(or_(User.username == data['username'], User.email == data['email'])).first()
            if exising_user:
                return set_response(None, 'User with email or username already exists', 400, False)

            user = user_schema.load(data)

            if avatar_file:
                avatar_url = upload_to_cloudinary(avatar_file, 'blog_app/avatars')
                user.avatar = avatar_url

            db.session.add(user)
            db.session.commit()
            return set_response(user_response_schema.dump(user), 'User registered successsfully', 200, True)

    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/update-username', methods=['POST'])
@jwt_required()
def update_username():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return set_response(None, 'Invalid data', 400, False)

            username = data['username']
            user_id = get_jwt_identity()
            print(f'USER ID : {user_id}')
            user = User.query.get(user_id)
            if not user:
                return set_response(None, 'User does not exist', 400, False)

            existing_user = User.query.filter(User.username == username, User.id != user_id).first()
            if existing_user:
                return set_response(None, 'username already exists', 400, False)

            user.username = username
            db.session.commit()
            return set_response(user_response_schema.dump(user), 'Username updated successfully', 200, True)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        if request.method == 'POST':
            data = request.get_json()
            old_password = data['old_password']
            new_password = data['new_password']
            user_id = get_jwt_identity()

            existing_user = User.query.get(user_id)
            if not existing_user:
                return set_response(None, 'User does not exist', 400, False)

            if existing_user.password != old_password:
                return set_response(None, 'Invalid credentials', 400, False)

            if existing_user.password == new_password:
                return set_response(None, 'New password must be different from old password', False)
        else:
            return set_response(None, 'Bad request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)