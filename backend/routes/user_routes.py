# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, session
from ..models import db, User
from .auth_routes import login_required, role_required
from functools import wraps

# Create blueprint for authentication users
user_bp = Blueprint('users', __name__)

def login_required(f):
    """
    Decorator to protect routes that require authentication
    Checks if user is logged in before allowing access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    """
    Decorator to protect routes that require specific roles
    Checks if user has the necessary permissions
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(session['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role != required_role and user.role != 'manager':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@user_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    POST /api/auth/register
    Expected JSON: {username, email, password, role}
    """
    try:
        data = request.get_json()
        
        # Update email if provided
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        # Only managers can change roles
        if 'role' in data and current_user.role == 'manager':
            user.role = data['role']
        
        # Update password if provided
        if 'password' in data and (current_user.id == user_id or current_user.role == 'manager'):
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('manager')
def delete_user(user_id):
    """
    Delete a user (manager only)
    DELETE /api/users/<user_id>
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user.id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/technicians', methods=['GET'])
@role_required('manager')
def get_technicians():
    """
    Get all technicians (for assigning tickets)
    GET /api/users/technicians
    """
    try:
        technicians = User.query.filter_by(role='technician').all()
        technicians_data = [user.to_dict() for user in technicians]
        
        return jsonify({
            'technicians': technicians_data,
            'count': len(technicians_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500