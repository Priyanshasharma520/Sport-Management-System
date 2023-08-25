from db import db
from flask import Flask, request, jsonify
from flask_smorest import Blueprint, abort
from models import Sport
from schemas import SportSchema, SportInputSchema, RegexFilterSchema
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blp = Blueprint("Sport", "sport", description="Operations on sport")

# Create a new sport
@blp.route('/sports', methods=['POST'])
@blp.arguments(SportSchema, location="json")
@blp.response(201, SportSchema)
def create_sport(sport_data):
    try:
    
        new_sport = Sport(**sport_data)
        db.session.add(new_sport)
        db.session.commit()
        return new_sport
    
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

# Search and filter sports
@blp.route('/sports/search', methods=['GET'])
@blp.arguments(SportInputSchema, location="query")
@blp.response(200, SportSchema(many=True))
def search_sports(data):
    try:
        query = Sport.query
        # Apply filters based on query parameters
        if 'name' in request.args:
            name_filter = request.args.get('name')
            query = query.filter(Sport.name == name_filter)

        if 'active' in request.args:
            active_filter = request.args.get('active').lower() == 'true'
            query = query.filter(Sport.active == active_filter)

        if 'slug' in request.args:
            slug_filter = request.args.get('slug')
            query = query.filter(Sport.slug == slug_filter)

        # Execute the query
        filtered_sports = query.all()
        return filtered_sports

    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        logger.error(e)
        abort(500, message=str(e))

# Route for regex-based sports filtering
@blp.route('/sports/regex', methods=['GET'])
@blp.arguments(RegexFilterSchema, location="query")
@blp.response(200, SportSchema(many=True))
def get_sports_by_regex(args):
    try:
        regex_pattern = args.get('regex_pattern')
        query = Sport.query.filter(Sport.name.op('REGEXP')(regex_pattern))
        matching_sports = query.all()
        return matching_sports
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        logger.error(e)
        abort(500, message=str(e))

# Route to get sports with a minimum threshold of active events
@blp.route('/sports/min_active_events/<int:min_threshold>', methods=['GET'])
@blp.response(200, SportSchema(many=True))
def get_sports_with_active_events_threshold(min_threshold):
    try:
        sports_with_active_events = []
        all_sports = Sport.query.all()
        for sport in all_sports:
            active_events_count = sum(1 for event in sport.events if event.active)
            if active_events_count >= min_threshold:
                sports_with_active_events.append(sport)

        return sports_with_active_events
    
    except ValueError as ve:
        logger.error(ve)
        abort(400, message=str(ve))
        
    except Exception as e:
        logger.error(e)
        abort(500, message=str(e))

# Update an sports
@blp.route('/sports/<int:sport_id>', methods=['PUT'])
@blp.arguments(SportInputSchema, location="json")
@blp.response(200, SportSchema)
def update_sport(sport_data, sport_id):
    try:
        sport = Sport.query.get_or_404(sport_id)

        if 'name' in sport_data:
            sport.name = sport_data['name']
        if 'slug' in sport_data:
            sport.slug = sport_data['slug']
        if 'active' in sport_data:
            sport.active = sport_data['active']

        db.session.add(sport)
        db.session.commit()

        return sport

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
