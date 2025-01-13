from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

api = Namespace('auth', description='Authentication operations')

@api.route('/register')
class Register(Resource):
    def post(self):
        data = request.get_json() or {}
        if 'username' not in data or 'email' not in data or 'password' not in data:
            return {'error': 'Must include username, email and password fields'}, 400
        
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Username already exists'}, 400
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already registered'}, 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()

        return {
            'username': user.username,
            'email': user.email,
            'message': 'User registered successfully'
        }, 201

@api.route('/login')
class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        if 'username' not in data or 'password' not in data:
            return {'error': 'Must include username and password fields'}, 400

        user = User.query.filter_by(username=data['username']).first()
        if user is None or not check_password_hash(user.password_hash, data['password']):
            return {'error': 'Invalid username or password'}, 401

        access_token = create_access_token(identity=user.id)
        return {
            'access_token': access_token,
            'username': user.username,
            'is_admin': user.is_admin
        }, 200

@api.route('/user')
class User(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return {
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }, 200
