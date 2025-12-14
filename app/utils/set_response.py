from flask import jsonify

def set_response(data, message, status_code, success):
    return jsonify({'data': data, 'status_code': status_code, 'success': success, 'message': message}), status_code