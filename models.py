from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(128), nullable=False, index=True) # Firebase UIDs can be long, indexed for performance
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    receipt_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    store_location = db.Column(db.String(255), nullable=True)
    insertion_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'totalAmount': self.total_amount,
            'receiptDate': self.receipt_date.isoformat() if self.receipt_date else None,
            'category': self.category,
            'notes': self.notes,
            'storeLocation': self.store_location,
            'insertionDate': self.insertion_date.isoformat() if self.insertion_date else None,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None,
            'isDeleted': self.is_deleted
        }
