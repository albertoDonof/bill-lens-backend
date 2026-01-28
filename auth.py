import os
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify, g
from functools import wraps

# Initialize Firebase Admin SDK
# Expects serviceAccountKey.json in the same directory
cred_path = os.environ.get('SERVICE_ACCOUNT_KEY_PATH') or os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

print(f"DEBUG: Starting Firebase Init")
print(f"DEBUG: Env Var SERVICE_ACCOUNT_KEY_PATH: '{os.environ.get('SERVICE_ACCOUNT_KEY_PATH')}'")
print(f"DEBUG: Resolved cred_path: '{cred_path}'")

if os.path.exists(cred_path):
    print("DEBUG: Credential file found!")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
else:
    print(f"WARNING: serviceAccountKey.json not found at '{cred_path}'. Firebase Auth will not work.")
    
    # Try to list the directory to see what's wrong (e.g. filename mismatch)
    try:
        if cred_path.startswith('/'):
            parent_dir = os.path.dirname(cred_path)
            if os.path.exists(parent_dir):
                print(f"DEBUG: Contents of {parent_dir}: {os.listdir(parent_dir)}")
            else:
                print(f"DEBUG: Parent directory {parent_dir} does not exist.")
    except Exception as e:
        print(f"DEBUG: Error listing directory: {e}")


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
