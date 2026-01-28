import os
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify, g
from functools import wraps

import json

# Initialize Firebase Admin SDK
# Expects serviceAccountKey.json in the same directory or in env var (path or content)
key_path_or_content = os.environ.get('SERVICE_ACCOUNT_KEY_PATH')
cred = None

print(f"DEBUG: Checking credentials configuration...")

if key_path_or_content and key_path_or_content.strip().startswith('{'):
    print("DEBUG: HOST detected JSON content in SERVICE_ACCOUNT_KEY_PATH env var.")
    try:
        cred_info = json.loads(key_path_or_content)
        cred = credentials.Certificate(cred_info)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON from env var: {e}")
else:
    # Treat as a file path
    cred_path = key_path_or_content or os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    print(f"DEBUG: Looking for credential file at: '{cred_path}'")
    
    if os.path.exists(cred_path):
        print("DEBUG: Credential file found!")
        cred = credentials.Certificate(cred_path)
    else:
        print(f"WARNING: serviceAccountKey.json not found at '{cred_path}'")

if cred:
    try:
        firebase_admin.initialize_app(cred)
        print("DEBUG: Firebase Admin initialized successfully.")
    except ValueError:
        print("DEBUG: Firebase App already initialized.")
else:
    print("CRITICAL: Firebase Auth will not work. No valid credentials found.")


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
