import requests
import json
import uuid
from datetime import datetime
import time

BASE_URL = 'http://localhost:5000/expenses'
HEADERS = {'Authorization': 'Bearer TEST_TOKEN'}

def test_create_expense():
    print("Testing Create Expense...")
    # Simulate offline creation with client-generated ID
    client_id = str(uuid.uuid4())
    data = {
        "id": client_id,
        "totalAmount": 100.50,
        "receiptDate": datetime.now().isoformat(),
        "category": "Food",
        "notes": "Lunch with team (Offline Created)"
    }
    response = requests.post(BASE_URL, json=data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return client_id

def test_get_expenses():
    print("\nTesting Get All Expenses (Active Only)...")
    response = requests.get(BASE_URL, headers=HEADERS)
    print(f"Status: {response.status_code}")
    # Print count only to avoid spam
    data = response.json()
    print(f"Count: {len(data)}")

def test_sync(since_timestamp):
    print(f"\nTesting Sync (Changes since {since_timestamp})...")
    response = requests.get(f"{BASE_URL}?since={since_timestamp}", headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_delete_expense(id):
    print(f"\nTesting Soft Delete Expense {id}...")
    response = requests.delete(f"{BASE_URL}/{id}", headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        print("Ensure the server is running on http://localhost:5000")
        
        # 1. Get current time for sync test later
        start_time = datetime.utcnow().isoformat()
        time.sleep(1) # Ensure some time passes
        
        # 2. Create Expense
        created_id = test_create_expense()
        
        # 3. Get All
        test_get_expenses()
        
        # 4. Test Sync (Should see the new expense)
        test_sync(start_time)
        
        # 5. Delete Expense
        if created_id:
            test_delete_expense(created_id)
            
        # 6. Get All (Should NOT see the deleted expense)
        test_get_expenses()
        
        # 7. Test Sync again (Should see the deleted expense with isDeleted=true)
        test_sync(start_time)

    except Exception as e:
        print(f"An error occurred: {e}")
