from app.extensions import db
from app.models.users import User
from app.schemas.user import UserSchema, UserResponseSchema, UserUpdatePasswordSchema
from app.utils.set_response import set_response
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import  check_password_hash, generate_password_hash

from app.utils.upload_to_cloudinary import upload_to_cloudinary


users_bp = Blueprint('users', __name__)
user_schema = UserSchema()
user_response_schema = UserResponseSchema()
user_update_password_schema = UserUpdatePasswordSchema()

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
            return set_response(user_response_schema.dump(user), 'User registered successfully', 200, True)

    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/update-username', methods=['PUT'])
@jwt_required()
def update_username():
    try:
        if request.method == 'PUT':
            data = request.get_json()
            if not data:
                return set_response(None, 'Invalid data', 400, False)

            username = data['username']
            user_id = get_jwt_identity()
            print(f'USER ID : {user_id}')
            user = User.query.get(user_id)
            if not user:
                return set_response(None, 'User does not exist', 400, False)

            if user.status == 'deleted':
                return set_response(None, 'User already deleted', 400, False)

            existing_user = User.query.filter(User.username == username, User.id != user_id).first()
            if existing_user:
                return set_response(None, 'username already exists', 400, False)

            user.username = username
            db.session.commit()
            return set_response(user_response_schema.dump(user), 'Username updated successfully', 200, True)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        if request.method == 'PUT':
            data = request.get_json()
            old_password = data['old_password']
            new_password = data['new_password']
            user_id = get_jwt_identity()

            existing_user = User.query.get(user_id)
            if not existing_user:
                return set_response(None, 'User does not exist', 400, False)

            if existing_user.status == 'deleted':
                return set_response(None, 'User deleted', 400, False)

            if not check_password_hash(existing_user.password, old_password):
                return set_response(None, 'Invalid credentials', 400, False)

            if check_password_hash(existing_user.password, new_password):
                return set_response(None, 'New password must be different from old password', 400, False)

            validate_password = user_update_password_schema.validate({'password': new_password})
            if validate_password:
                return set_response(None, str(validate_password), 400, False)

            existing_user.password = generate_password_hash(new_password)
            db.session.commit()
            return set_response(user_response_schema.dump(existing_user), 'Password updated successfully', 200, True)
        else:
            return set_response(None, 'Bad request', 400, False)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/delete-user', methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        if request.method == 'DELETE':
            user_id = get_jwt_identity()

            if not user_id:
                return set_response(None, 'User does not exist', 400, False)

            user = User.query.get(user_id)
            if not user:
                return set_response(None, 'User does not exist', 400, False)

            if user.status == 'deleted':
                return set_response(None, 'User already deleted', 400, False)

            user.status = 'deleted'
            db.session.commit()
            return set_response(None, 'User deleted successfully', 200, True)
        else:
            return set_response(None, 'Bad request', 400, False)

    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/update-avatar', methods=['PUT'])
@jwt_required()
def update_avatar():
    try:
        if request.method == 'PUT':
            user_id = get_jwt_identity()
            avatar = request.files.get('avatar')

            if not user_id:
                return set_response(None, 'User does not exist', 400, False)

            if not avatar:
                return set_response(None, 'Invalid avatar', 400, False)

            existing_user = User.query.get(user_id)
            if not existing_user:
                return set_response(None, 'User does not exist', 400, False)

            if existing_user.status == 'deleted':
                return set_response(None, 'User already deleted', 400, False)

            cloudinary_resp = upload_to_cloudinary(avatar, 'blog_app/avatars')
            if not cloudinary_resp:
                return set_response(None, 'Error while uploading avatar', 400, False)

            existing_user.avatar = cloudinary_resp
            db.session.commit()
            return set_response(user_response_schema.dump(existing_user), 'Avatar updated successfully', 200, True)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)


@users_bp.route('/get-user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        if request.method == 'GET':
            jwt_user_identity = int(get_jwt_identity())
            print(f'user_id type : {type(user_id)}')
            print(f'jwt identity type : {type(jwt_user_identity)}')
            if user_id != jwt_user_identity:
                return set_response(None, 'Invalid user id', 400, False)

            user = User.query.get(user_id)
            if not user:
                return set_response(None, 'User does not exist', 400, False)

            if user.status == 'deleted':
                return set_response(None, 'User already deleted', 400, False)
            return set_response(user_response_schema.dump(user), 'User retrieved successfully', 200, True)
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)