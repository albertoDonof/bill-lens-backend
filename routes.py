from flask import Blueprint, request, jsonify, g
from models import db, Expense
from datetime import datetime, timedelta
from sqlalchemy import extract, func
import uuid
from auth import login_required

bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@bp.route('', methods=['POST'])
@login_required
def create_expense():
    data = request.get_json()
    try:
        # Parse receiptDate. Assuming ISO format or similar from the app
        receipt_date = datetime.fromisoformat(data['receiptDate'].replace('Z', '+00:00'))
        
        # Check if ID is provided (offline creation), else generate
        expense_id = data.get('id')
        if not expense_id:
            expense_id = str(uuid.uuid4())
            
        # Check if exists (upsert logic for sync)
        # MUST filter by user_id to ensure we don't overwrite someone else's expense (though UUIDs should be unique)
        existing = Expense.query.filter_by(id=expense_id, user_id=g.user_id).first()
        
        if existing:
            existing.total_amount = data['totalAmount']
            existing.receipt_date = receipt_date
            existing.category = data['category']
            existing.notes = data.get('notes')
            existing.store_location = data.get('storeLocation')
            if 'isDeleted' in data:
                existing.is_deleted = data['isDeleted']
            else:
                existing.is_deleted = False
            new_expense = existing
        else:
            new_expense = Expense(
                id=expense_id,
                user_id=g.user_id,
                total_amount=data['totalAmount'],
                receipt_date=receipt_date,
                category=data['category'],
                notes=data.get('notes'),
                store_location=data.get('storeLocation')
            )
            db.session.add(new_expense)
            
        db.session.commit()
        return jsonify(new_expense.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('', methods=['GET'])
@login_required
def get_expenses():
    since = request.args.get('since')
    # Filter by current user
    query = Expense.query.filter_by(user_id=g.user_id)
    
    if since:
        try:
            since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
            query = query.filter(Expense.last_updated > since_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format for since parameter'}), 400
    else:
        # If not syncing, return only active expenses
        query = query.filter(Expense.is_deleted == False)
        
    expenses = query.all()
    return jsonify([e.to_dict() for e in expenses])

@bp.route('/<string:id>', methods=['GET'])
@login_required
def get_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=g.user_id).first_or_404()
    return jsonify(expense.to_dict())

@bp.route('/<string:id>', methods=['DELETE'])
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=g.user_id).first_or_404()
    expense.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Expense deleted', 'id': id})

@bp.route('/monthly/<int:year>/<int:month>', methods=['GET'])
@login_required
def get_monthly_expenses(year, month):
    expenses = Expense.query.filter(
        Expense.user_id == g.user_id,
        extract('year', Expense.receipt_date) == year,
        extract('month', Expense.receipt_date) == month,
        Expense.is_deleted == False
    ).all()
    return jsonify([e.to_dict() for e in expenses])

@bp.route('/analytics/last-month', methods=['GET'])
@login_required
def get_last_month_analytics():
    today = datetime.today()
    # Calculate first day of current month
    first_day_current_month = today.replace(day=1)
    # Calculate last day of previous month
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    # Calculate first day of previous month
    first_day_prev_month = last_day_prev_month.replace(day=1)

    results = db.session.query(
        Expense.category,
        func.sum(Expense.total_amount)
    ).filter(
        Expense.user_id == g.user_id,
        Expense.receipt_date >= first_day_prev_month,
        Expense.receipt_date <= last_day_prev_month,
        Expense.is_deleted == False
    ).group_by(Expense.category).all()

    return jsonify({category: amount for category, amount in results})
