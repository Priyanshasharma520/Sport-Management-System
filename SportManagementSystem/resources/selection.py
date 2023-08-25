from flask import Flask, request, jsonify, url_for ,current_app
from flask_smorest import Blueprint, abort
from models import Selection ,Event
from static import SelectionOutcome
from static import activate_event,deactivate_event
from db import db
import requests
from schemas import  SelectionSchema , SelectionSchemaOutput ,SelectionSearchSchema ,RegexFilterSchema ,SelectionUpdateSchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blp = Blueprint("Selection", "selection", description="Operations on selection")

# Create a new selection
@blp.route('/selections', methods=['POST'])
@blp.arguments(SelectionSchema,location="json")
@blp.response(201,SelectionSchemaOutput)
def create_selection(selection_data):
    try:
        
        # validate event_id is present or not
        event_id = selection_data.get("event_id")
        existing_event = Event.query.get(event_id)
        if not existing_event or not existing_event.active:
            abort(400, message="Invalid event_id provided")

        new_selection = Selection(**selection_data)
        db.session.add(new_selection)
        db.session.commit()
        return new_selection, 201
    
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
        
# Update a selection
@blp.route('/selections/<int:selection_id>', methods=['PUT'])
@blp.arguments(SelectionUpdateSchema)
@blp.response(201,SelectionSchemaOutput)
def update_selection(selection_data,selection_id):
    try:
        selection = Selection.query.get_or_404(selection_id)
        
        if 'price' in selection_data:
            selection.price = float(selection_data['price'])  # Convert to float
        if 'name' in selection_data:
            selection.name = selection_data['name']
        if 'outcome' in selection_data:
            selection.outcome = SelectionOutcome(selection_data['outcome'])
        if 'active' in selection_data:
            if selection_data['active']:
                # Activate the selection
                selection.active = True
                event = selection.event
                if not event.active:
                    activate_event(event)
            else:
                # Deactivate the selection
                selection.active = False
                # Check if all selections of the event are inactive
                event = selection.event
                if all(not s.active for s in event.selections):
                    deactivate_event(event)

        db.session.add(selection)
        db.session.commit()
        
        return selection
    
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
# Search and filter selections
@blp.route('/selections/search', methods=['GET'])
@blp.arguments(SelectionSearchSchema,location="query")
@blp.response(201,SelectionSchemaOutput(many=True))
def search_selections(data):
    try:
        
        query = Selection.query
        # Apply filters based on query parameters
        if 'name' in request.args:
            name_filter = request.args.get('name')
            query = query.filter(Selection.name == name_filter)

        if 'price' in request.args:
            price_filter = float(request.args.get('price'))
            query = query.filter(Selection.price == price_filter)

        if 'active' in request.args:
            active_filter = request.args.get('active').lower() == 'true'
            query = query.filter(Selection.active == active_filter)

        if 'outcome' in request.args:
            outcome_filter = request.args.get('outcome')
            query = query.filter(Selection.outcome == outcome_filter)
            
        if 'event_id' in request.args:
            event_id_filter = request.args.get('event_id')
            query = query.filter(Selection.event_id == event_id_filter)
        
        filtered_selections = query.all()

        return filtered_selections
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        abort(500, description=str(e))
        
# Route for regex-based selections filtering
@blp.route('/selections/regex', methods=['GET'])
@blp.arguments(RegexFilterSchema, location="query")
@blp.response(200, SelectionSchemaOutput(many=True))
def get_selection_by_regex(args):
    try:
        regex_pattern = args.get('regex_pattern')
        query = Selection.query.filter(Selection.name.op('REGEXP')(regex_pattern))
        matching_selections = query.all()
        return matching_selections
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
    except Exception as e:
        abort(500, description=str(e))