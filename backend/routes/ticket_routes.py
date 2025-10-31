# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, session
from ..models import db, Ticket, User, ActivityLog
from .auth_routes import login_required, role_required
from functools import wraps
from datetime import datetime

# Create blueprint for ticket routes
ticket_bp = Blueprint('tickets', __name__)


@ticket_bp.route('', methods=['GET'])
@login_required
def get_tickets():
    """
    Get all tickets (filtered by user role)
    GET /api/tickets
    Query parameters: status, priority, assigned_to
    """
    try:
        user = User.query.get(session['user_id'])
        
        # Start with base query
        query = Ticket.query
        
        # Filter based on user role
        if user.role == 'user':
            # Regular users only see their own tickets
            query = query.filter_by(created_by=user.id)
        elif user.role == 'technician':
            # Technicians see tickets assigned to them
            query = query.filter_by(assigned_to=user.id)
        # Managers see all tickets (no filter)
        
        # Apply additional filters from query parameters
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        priority = request.args.get('priority')
        if priority:
            query = query.filter_by(priority=priority)
        
        assigned_to = request.args.get('assigned_to')
        if assigned_to:
            query = query.filter_by(assigned_to=assigned_to)
        
        # Execute query and convert to list of dictionaries
        tickets = query.order_by(Ticket.created_at.desc()).all()
        tickets_data = [ticket.to_dict() for ticket in tickets]
        
        return jsonify({
            'tickets': tickets_data,
            'count': len(tickets_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    """
    Get a specific ticket by ID
    GET /api/tickets/<ticket_id>
    """
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        user = User.query.get(session['user_id'])
        
        # Check permissions
        if user.role == 'user' and ticket.created_by != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        if user.role == 'technician' and ticket.assigned_to != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get activity logs for this ticket
        activities = ActivityLog.query.filter_by(ticket_id=ticket_id).order_by(ActivityLog.created_at.desc()).all()
        activities_data = [activity.to_dict() for activity in activities]
        
        return jsonify({
            'ticket': ticket.to_dict(),
            'activities': activities_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('', methods=['POST'])
@login_required
def create_ticket():
    """
    Create a new ticket
    POST /api/tickets
    Expected JSON: {title, description, category, priority}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new ticket
        ticket = Ticket(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data.get('priority', 'medium'),
            created_by=session['user_id']
        )
        
        db.session.add(ticket)
        db.session.flush()  # Get ticket ID before committing
        
        # Create activity log
        activity = ActivityLog(
            ticket_id=ticket.id,
            user_id=session['user_id'],
            action='created',
            description=f'Ticket created: {ticket.title}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': ticket.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    """
    Update an existing ticket
    PUT /api/tickets/<ticket_id>
    Expected JSON: {status, priority, assigned_to, etc.}
    """
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        # Track changes for activity log
        changes = []
        
        # Update allowed fields
        if 'title' in data and user.role in ['manager', 'technician']:
            ticket.title = data['title']
            changes.append(f'Title changed to: {data["title"]}')
        
        if 'description' in data and user.role in ['manager', 'technician']:
            ticket.description = data['description']
            changes.append('Description updated')
        
        if 'priority' in data and user.role in ['manager', 'technician']:
            old_priority = ticket.priority
            ticket.priority = data['priority']
            changes.append(f'Priority changed from {old_priority} to {data["priority"]}')
        
        if 'status' in data and user.role in ['manager', 'technician']:
            old_status = ticket.status
            ticket.status = data['status']
            changes.append(f'Status changed from {old_status} to {data["status"]}')
            
            # If status is resolved or closed, set resolved_at timestamp
            if data['status'] in ['resolved', 'closed'] and not ticket.resolved_at:
                ticket.resolved_at = datetime.utcnow()
        
        if 'assigned_to' in data and user.role == 'manager':
            old_assigned = ticket.assigned_to
            ticket.assigned_to = data['assigned_to']
            
            if old_assigned:
                changes.append(f'Reassigned from user {old_assigned} to user {data["assigned_to"]}')
            else:
                changes.append(f'Assigned to user {data["assigned_to"]}')
        
        ticket.updated_at = datetime.utcnow()
        
        # Create activity log for each change
        for change in changes:
            activity = ActivityLog(
                ticket_id=ticket.id,
                user_id=session['user_id'],
                action='updated',
                description=change
            )
            db.session.add(activity)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket updated successfully',
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@role_required('manager')
def delete_ticket(ticket_id):
    """
    Delete a ticket (manager only)
    DELETE /api/tickets/<ticket_id>
    """
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({'message': 'Ticket deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/stats', methods=['GET'])
@role_required('manager')
def get_ticket_stats():
    """
    Get ticket statistics (manager only)
    GET /api/tickets/stats
    """
    try:
        total_tickets = Ticket.query.count()
        open_tickets = Ticket.query.filter_by(status='open').count()
        in_progress_tickets = Ticket.query.filter_by(status='in_progress').count()
        resolved_tickets = Ticket.query.filter_by(status='resolved').count()
        closed_tickets = Ticket.query.filter_by(status='closed').count()
        
        high_priority = Ticket.query.filter_by(priority='high').count()
        critical_priority = Ticket.query.filter_by(priority='critical').count()
        
        return jsonify({
            'total_tickets': total_tickets,
            'by_status': {
                'open': open_tickets,
                'in_progress': in_progress_tickets,
                'resolved': resolved_tickets,
                'closed': closed_tickets
            },
            'high_priority_tickets': high_priority,
            'critical_tickets': critical_priority
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500