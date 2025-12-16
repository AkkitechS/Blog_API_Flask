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
@jwt_required
def update_username():
    try:
        pass
    except Exception as e:
        print(e)
        return set_response(None, str(e), 500, False)