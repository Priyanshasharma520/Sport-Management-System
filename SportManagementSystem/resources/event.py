
from flask import Flask, request, jsonify , current_app , url_for
from flask_smorest import Blueprint, abort
from models import Event,Sport
from static import EventType , EventStatus
from static import update_sport_status
from datetime import datetime
from schemas import  EventSchema , EventSchemaOutput , EventSearchSchema ,EventUpdateSchema, ActivateDeactivateEvent ,RegexFilterSchema
from flask_sqlalchemy import SQLAlchemy
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blp = Blueprint("Event", "event", description="Operations on event")

# Create a new event
@blp.route('/events', methods=['POST'])
@blp.arguments(EventSchema,location="json")
@blp.response(201,EventSchemaOutput)
def create_event(event_data):
    try:
        # validate sport_id is present or not
        sport_id = event_data.get("sport_id")
        existing_sport = Sport.query.get(sport_id)
        if not existing_sport or not existing_sport.active:
            abort(400, message="Invalid sport_id provided")

        new_event = Event(**event_data)
        db.session.add(new_event)
        db.session.commit()
        return new_event, 201
    
    except SQLAlchemyError as sae:
        db.session.rollback()
        error_message = "An SQLAlchemy error occurred: " + str(sae)
        logger.error(error_message)
        abort(500, message=error_message)
    
    except ValidationError as vee:
        db.session.rollback()
        error_messages = vee.messages
        logger.error(error_messages)
        abort(400, message=error_messages)
            
    except ValueError as ve:
        db.session.rollback()
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        abort(500, message=str(e))

# Update an event
@blp.route('/events/<int:event_id>', methods=['PUT'])
@blp.arguments(EventUpdateSchema)
@blp.response(201,EventSchemaOutput)
def update_event(event_data,event_id):

    try:
        event = Event.query.get_or_404(event_id)
        
        if not event.active :
            abort(400, message="Cannot update inactive event")
        
        if 'type' in event_data:
            event.type = EventType(event_data['type'])
        if 'status' in event_data:
            old_status = event.status
            new_status = EventStatus(event_data['status'])
            event.status = new_status
            
            # Check if the status changed to "STARTED"
            if new_status == EventStatus.STARTED and old_status != EventStatus.STARTED:
                event.actual_start = datetime.utcnow()  # Update actual_start time
                
        if 'name' in event_data:
            event.name = event_data['name']
        if 'slug' in event_data:
            event.slug = event_data['slug']
            
        if 'scheduled_start' in event_data:
            event.scheduled_start = event_data['scheduled_start']

        db.session.add(event)
        db.session.commit()
        return event
    
    except SQLAlchemyError as sae:
        db.session.rollback()
        error_message = "An SQLAlchemy error occurred: " + str(sae)
        logger.error(error_message)
        abort(500, message=error_message)
    
    except ValidationError as vee:
        db.session.rollback()
        error_messages = vee.messages
        logger.error(error_messages)
        abort(400, message=error_messages)
            
    except ValueError as ve:
        db.session.rollback()
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        abort(500, message=str(e))


# Search and filter events
@blp.route('/events/search', methods=['GET'])
@blp.arguments(EventSearchSchema,location="query")
@blp.response(201,EventSchemaOutput(many=True))
def search_events(data):
    try:
        query = Event.query

        # Apply filters based on query parameters
        if 'name' in request.args:
            name_filter = request.args.get('name')
            query = query.filter(Event.name == name_filter)

        if 'status' in request.args:
            status_filter = request.args.get('status')
            query = query.filter(Event.status == status_filter)

        if 'type' in request.args:
            type_filter = request.args.get('type')
            query = query.filter(Event.type == type_filter)

        if 'slug' in request.args:
            slug_filter = request.args.get('slug')
            query = query.filter(Event.slug == slug_filter)

        if 'active' in request.args:
            active_filter = request.args.get('active').lower() == 'true'
            query = query.filter(Event.active == active_filter)

        if 'sport_id' in request.args:
            type_filter = request.args.get('sport_id')
            query = query.filter(Event.sport_id == type_filter)

        if 'scheduled_start_from' in request.args:
            scheduled_start_from_filter = request.args.get('scheduled_start_from')
            query = query.filter(Event.scheduled_start >= scheduled_start_from_filter)

        if 'scheduled_start_to' in request.args:
            scheduled_start_to_filter = request.args.get('scheduled_start_to')
            query = query.filter(Event.scheduled_start <= scheduled_start_to_filter)

        if 'actual_start_from' in request.args:
            actual_start_from_filter = request.args.get('actual_start_from')
            query = query.filter(Event.actual_start >= actual_start_from_filter)

        if 'actual_start_to' in request.args:
            actual_start_to_filter = request.args.get('actual_start_to')
            query = query.filter(Event.actual_start <= actual_start_to_filter)

        # Add more filters as needed...

        # Execute the query
        filtered_events = query.all()
        return filtered_events
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        logger.error(e)
        abort(500, message=str(e))

# Route for regex-based event filtering        
@blp.route('/events/regex', methods=['GET'])
@blp.arguments(RegexFilterSchema, location="query")
@blp.response(200, EventSchemaOutput(many=True))
def get_events_by_regex(args):
    try:
        regex_pattern = args.get('regex_pattern')
        query = Event.query.filter(Event.name.op('REGEXP')(regex_pattern))
        matching_events = query.all()
        return matching_events
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        logger.error(e)
        abort(500, message=str(e))

# Route to get events with a minimum threshold of active selections
@blp.route('/events/min_active_events/<int:min_threshold>', methods=['GET'])
@blp.response(200, EventSchemaOutput(many=True))
def get_events_with_active_selections_threshold(min_threshold):
    try:
        events_with_active_events = []
        all_events = Event.query.all()
        for event in all_events:
            active_selections_count = sum(1 for selection in event.selections if selection.active)
            if active_selections_count >= min_threshold:
                events_with_active_events.append(event)

        return events_with_active_events
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        abort(500, description=str(e))
        
        
# Activate or deactivate an event
@blp.route('/events/<int:event_id>/activate-deactivate', methods=['PUT'])
@blp.arguments(ActivateDeactivateEvent)
@blp.response(201, EventSchemaOutput)
def activate_deactivate_event(event_data, event_id):
    try:
        event = Event.query.get_or_404(event_id)
        new_active_status = event_data.get('active')

        if new_active_status is not None and new_active_status != event.active:
            event.active = new_active_status
            db.session.add(event)
            db.session.commit()

            sport = event.sport
            all_sport_events_active = all(e.active for e in sport.events)
            all_sport_events_inactive = all(not e.active for e in sport.events)

            if all_sport_events_active and not sport.active:
                update_sport_status(sport, True)
            elif all_sport_events_inactive and sport.active:
                update_sport_status(sport, False)

        return event
    
    except SQLAlchemyError as sae:
        db.session.rollback()
        error_message = "An SQLAlchemy error occurred: " + str(sae)
        logger.error(error_message)
        abort(500, message=error_message)
    
    except ValidationError as vee:
        db.session.rollback()
        error_messages = vee.messages
        logger.error(error_messages)
        abort(400, message=error_messages)
            
    except ValueError as ve:
        db.session.rollback()
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        abort(500, message=str(e))




