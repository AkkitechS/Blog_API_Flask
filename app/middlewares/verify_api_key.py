from flask import request, current_app
from functools import wraps
from app.utils.set_response import set_response

def verify_api_key():
    api_key = request.headers.get('X-api-key')
    print(f'api_key: {api_key}')
    print(f'current_app: {current_app}')

    if not api_key:
        return set_response(None, 'Unauthorized access', 401, False)

    if not api_key == current_app.config.get('SECRET_KEY'):
        return set_response(None, 'Unauthorized access', 401, False)