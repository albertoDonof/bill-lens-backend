import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/bill_lens'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
