from flask import Blueprint, jsonify, g, request
from models import Expense
import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials
import os
from datetime import datetime
from auth import login_required

bp = Blueprint('export', __name__, url_prefix='/api/export')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_gspread_client():
    cred_path = os.environ.get('SERVICE_ACCOUNT_KEY_PATH') or os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    if not os.path.exists(cred_path):
        raise Exception("serviceAccountKey.json not found")
    
    credentials = ServiceAccountCredentials.from_service_account_file(cred_path, scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client

@bp.route('/sheets', methods=['POST'])
@login_required
def export_to_sheets():
    if not g.user_email:
        return jsonify({'error': 'User email not found in token.'}), 400

    request_data = request.get_json() or {}
    user_access_token = request_data.get('accessToken')
    print("User access token ricevuto: ", user_access_token)

    try:
        # 1. Fetch Expenses
        expenses = Expense.query.filter_by(user_id=g.user_id, is_deleted=False).order_by(Expense.receipt_date.desc()).all()
        
        if not expenses:
            return jsonify({'message': 'No expenses to export'}), 200

        # 2. Prepare Data
        headers = ['Date', 'Category', 'Amount', 'Store Location', 'Notes']
        data = []
        for e in expenses:
            data.append([
                e.receipt_date.strftime('%Y-%m-%d'),
                e.category,
                float(e.total_amount),
                e.store_location or "",
                e.notes or ""
            ])

        # 3. Authenticate with Google
        if user_access_token:
            # Use User's Credentials (creates file in User's Drive)
            creds = Credentials(token=user_access_token)
            gc = gspread.authorize(creds)
            print(f"Exporting as User: {g.user_email}")
        else:
            # Fallback to Service Account (creates in Bot's Drive and shares)
            gc = get_gspread_client()
            print("Exporting as Service Account (Fallback)")

        # 4. Create Google Sheet
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        sheet_title = f"Bill Lens Expenses - {current_time}"
        
        sh = gc.create(sheet_title)
        worksheet = sh.get_worksheet(0)
        
        # 5. Write Data
        worksheet.append_row(headers)
        if data:
            worksheet.append_rows(data)
            
        try:
            worksheet.format('A1:E1', {'textFormat': {'bold': True}})
        except:
            pass

        # 6. Share/Return
        response_data = {
            'message': 'Sheet created successfully',
            'sheetUrl': sh.url,
            'sheetTitle': sheet_title
        }

        if user_access_token:
             # Created in User's Drive, strictly speaking we don't need to share it with them, they own it.
             response_data['sharedWith'] = 'Owner (You)'
        else:
            # Created by Service Account, must share
            sh.share(g.user_email, perm_type='user', role='writer')
            response_data['sharedWith'] = g.user_email

        return jsonify(response_data), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Export Error: {e}")
        return jsonify({'error': 'Failed to export to Sheets.', 'details': str(e)}), 500
