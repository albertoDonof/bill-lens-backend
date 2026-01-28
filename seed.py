from app import app, db
from models import Expense
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta

fake = Faker()

CATEGORIES = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'Shopping']

def seed_data(num_entries=50):
    print(f"Seeding {num_entries} expenses...")
    with app.app_context():
        for _ in range(num_entries):
            # Random date within the last year
            receipt_date = fake.date_time_between(start_date='-1y', end_date='now')
            
            expense = Expense(
                id=str(uuid.uuid4()),
                user_id='test_user_id', # Dummy user ID for seeding
                total_amount=round(random.uniform(5.0, 500.0), 2),
                receipt_date=receipt_date,
                category=random.choice(CATEGORIES),
                notes=fake.sentence(),
                store_location=fake.address(),
                insertion_date=receipt_date + timedelta(minutes=random.randint(1, 60)) # Inserted shortly after receipt
            )
            db.session.add(expense)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
