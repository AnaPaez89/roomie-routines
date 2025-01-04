from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Enum("admin", "tenant", name="user_roles"), nullable=False)
    photo_url = db.Column(db.String(), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    invitations_sent = db.relationship('Invitations', backref='admin', lazy=True)

    def __repr__(self):
        return f'<User {self.id} - {self.email}>'

    def serialize(self):
        return {'id': self.id,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role,
                'photo_url': self.photo_url}


class Homes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin = db.relationship('Users', backref=db.backref('managed_homes', lazy=True))

    def __repr__(self):
        return f'<Home {self.id} - {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'admin_id': self.admin_id
        }


class Memberships(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    home_id = db.Column(db.Integer, db.ForeignKey('homes.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('memberships', lazy=True))
    home = db.relationship('Homes', backref=db.backref('members', lazy=True))

    def __repr__(self):
        return f'<Membership User {self.user_id} in Home {self.home_id}>'

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'home_id': self.home_id
        }


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_user = db.relationship('Users', backref=db.backref('assigned_tasks', lazy=True))
    home_id = db.Column(db.Integer, db.ForeignKey('homes.id'), nullable=False)
    home = db.relationship('Homes', backref=db.backref('tasks', lazy=True))
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.id} - {self.title}>'

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'assigned_to': self.assigned_to,
            'home_id': self.home_id,
            'is_completed': self.is_completed
        }


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('Users', backref=db.backref('notifications', lazy=True))
    task = db.relationship('Tasks', backref=db.backref('notifications', lazy=True))

    def __repr__(self):
        return f'<Notification {self.id} - User {self.user_id} for Task {self.task_id}>'

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'is_read': self.is_read,
            'sent_at': self.sent_at
        }

class Invitations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    home_id = db.Column(db.Integer, db.ForeignKey('homes.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    home = db.relationship('Homes', backref=db.backref('invitations', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Invitation {self.id} - {self.email} for Home {self.home_id}>'

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'home_id': self.home_id,
            'status': self.status
        }

