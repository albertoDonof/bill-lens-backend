import os
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify, g
from functools import wraps

# Initialize Firebase Admin SDK
# Expects serviceAccountKey.json in the same directory
cred_path = os.environ.get('SERVICE_ACCOUNT_KEY_PATH') or os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
else:
    print("WARNING: serviceAccountKey.json not found. Firebase Auth will not work correctly.")
    # For development/testing without firebase credentials, we might want a mock mode
    # But strictly speaking, we should warn.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Bypass for testing if configured (e.g. via env var)
        if os.environ.get('FLASK_ENV') == 'testing' and request.headers.get('Authorization') == 'Bearer TEST_TOKEN':
            g.user_id = 'test_user_id'
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        try:
            # Header format: "Bearer <token>"
            token = auth_header.split(" ")[1]
            # Verify the token
            decoded_token = auth.verify_id_token(token)
            # Add user ID and Email to global context
            g.user_id = decoded_token['uid']
            g.user_email = decoded_token.get('email')
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function
