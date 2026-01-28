from app import app
from export_routes import get_gspread_client
import gspread

def clean_drive():
    print("Authenticating with Service Account...")
    try:
        gc = get_gspread_client()
    except Exception as e:
        print(f"Error authenticating: {e}")
        return

    print("Listing all spreadsheet files owned by Service Account...")
    try:
        # List all spreadsheets
        files = gc.list_spreadsheet_files()
        print(f"Found {len(files)} spreadsheets.")
        
        if not files:
            print("Drive is already empty.")
            return

        print("Deleting files...")
        for f in files:
            try:
                print(f"Deleting: {f['name']} (ID: {f['id']})")
                gc.del_spreadsheet(f['id'])
            except Exception as e:
                print(f"Failed to delete {f['name']}: {e}")
        
    except Exception as e:
        print(f"Error listing/deleting files: {e}")

if __name__ == '__main__':
    # Push app context just in case, though gspread logic here is mostly independent
    with app.app_context():
        clean_drive()
