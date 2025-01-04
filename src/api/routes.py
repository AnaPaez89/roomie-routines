"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from api.models import db, Users, Homes, Memberships, Tasks, Notifications, Invitations
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity


api = Blueprint('api', __name__)
CORS(api)  # Allow CORS requests to this API


@api.route('/hello', methods=['GET'])
def handle_hello():
    response_body = {}
    response_body["message"]= "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    return response_body, 200


@api.route('/signup', methods=['POST'])
def signup():
    response_body = {}
    data = request.json
    new_user = Users(
        email = data.get('email'),
        password = data.get('password'),
        first_name = data.get('first_name'),
        last_name = data.get('last_name'),
        role = 'admin',  
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()
    response_body['message'] = "Registration succeeded!"
    response_body['results'] = new_user.serialize()
    return jsonify(response_body), 200


@api.route('/send_invitation', methods=['POST'])
@jwt_required() 
def send_invitation():
    response_body = {}
    data = request.json
    admin_id = get_jwt_identity()
    admin = Users.query.get(admin_id)
    if not admin or admin.role != 'admin':
        response_body['message'] = "Only admins can send invitations."
        return jsonify(response_body), 403
    new_invitation = Invitations(
        email=data.get('email'),
        home_id=data.get('home_id'),
    )
    db.session.add(new_invitation)
    db.session.commit()
    response_body['message'] = "Invitation sent successfully!"
    response_body['invitation'] = new_invitation.serialize()
    return jsonify(response_body), 200


@api.route('/accept_invitation', methods=['POST'])
def accept_invitation():
    response_body = {}
    data = request.json
    invitation = Invitations.query.filter_by(email=data.get('email'), status='pending').first()
    if not invitation:
        response_body['message'] = "No valid invitation found or invitation already accepted."
        return jsonify(response_body), 400
    new_user = Users(
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role='tenant',
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()
    invitation.status = 'accepted'
    db.session.commit()
    new_membership = Memberships(user_id=new_user.id, home_id=invitation.home_id)
    db.session.add(new_membership)
    db.session.commit()
    response_body['message'] = "User registered successfully!"
    response_body['user'] = new_user.serialize()
    return jsonify(response_body), 200

