from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from routes import bp as expenses_bp
from export_routes import bp as export_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(expenses_bp)
app.register_blueprint(export_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
