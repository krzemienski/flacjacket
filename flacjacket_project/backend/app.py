from flask import Flask
from routes.analyze import analyze_bp
from routes.history import history_bp
from db_setup import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres:5432/flacjacket'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(analyze_bp, url_prefix='/api')
app.register_blueprint(history_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)