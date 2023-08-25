
from marshmallow import fields, validate, Schema
from models import Sport , Event, Selection
from static import EventType , EventStatus
from static import SelectionOutcome
from flask import jsonify
from webargs import fields, validate

# Define a custom field for handling enum values as strings
class EnumStringField(fields.String):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value

# Schema for Sport model    
class SportSchema(Schema):
    class Meta:
        model = Sport  # Specify the model for the schema
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    active = fields.Bool(dump_only=True, validate=validate.OneOf([True, False]))

# Input schema for creating/updating a Sport    
class SportInputSchema(Schema):
    class Meta:
        model = Sport  # Specify the model for the schema
    name = fields.String()
    slug = fields.String()
    active = fields.Bool(required=False, validate=validate.OneOf([True, False]))

# Schema for Event model
class EventSchema(Schema):
    class Meta:
        model = Event  # Specify the model for the schema
    
    id = fields.Int(dump_only=True)
    type = fields.String(
        required=True,
        validate=validate.OneOf([e.value for e in EventType])
    )
    
    status = fields.String(
        required=True,
        validate=validate.OneOf([e.value for e in EventStatus])
    )
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    active = fields.Bool(dump_only=True, validate=validate.OneOf([True, False]))
    scheduled_start = fields.DateTime(required=True,format='%Y-%m-%dT%H:%M:%S.%fZ')
    actual_start = fields.DateTime(format='%Y-%m-%dT%H:%M:%S.%fZ', allow_none=True)
    sport_id = fields.Int(required=True, load_only=True)
    sport = fields.Nested(SportSchema(), dump_only=True)
    
# Schema for displaying Event information in the response
class EventSchemaOutput(EventSchema):

    # You can also explicitly define the fields you want to include in the schema
    
    status = EnumStringField(attribute='status')
    type = EnumStringField(attribute='type')
    sport_id = fields.Int(dump_only=True)
    
# Schema for searching/filtering Events
class EventSearchSchema(Schema):
    class Meta:
        model = Event  # Specify the model for the schema
    
    name = fields.Str(validate=validate.Length(max=255))
    slug = fields.Str(validate=validate.Length(max=255))
    active = fields.Bool(validate=validate.OneOf([True, False]))
    type = fields.Str(validate=validate.OneOf(["PREPLAY", "INPLAY"]))
    status = fields.Str(validate=validate.OneOf(["PENDING", "STARTED", "ENDED", "CANCELLED"]))
    sport_id = fields.Int()
    scheduled_start_from = fields.DateTime()
    scheduled_start_to = fields.DateTime()
    actual_start_from = fields.DateTime()
    actual_start_to = fields.DateTime()

# Schema for updating an Event
class EventUpdateSchema(Schema):
    class Meta:
        model = Event  # Specify the model for the schema
    
    name = fields.Str(required=False)
    slug = fields.Str(required=False)
    type = fields.Str(required=False ,validate=validate.OneOf(["PREPLAY", "INPLAY"]))
    status = fields.Str(required=False ,validate=validate.OneOf(["PENDING", "STARTED", "ENDED", "CANCELLED"]))
    scheduled_start = fields.DateTime(format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
    actual_start = fields.DateTime( format='%Y-%m-%dT%H:%M:%S.%fZ', allow_none=True, required=False)

# Schema for activating/deactivating an Event        
class ActivateDeactivateEvent(Schema):
    class Meta:
        model = Event
     
    active = fields.Bool(required=True)   
    
# Schema for Selection model        
class SelectionSchema(Schema):
    
    class Meta:
        model = Selection

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Decimal(as_string=True, required=True, places=2)
    active = fields.Bool(dump_only=True, validate=validate.OneOf([True, False]))
    outcome = fields.String(
        validate=validate.OneOf([e.value for e in SelectionOutcome])
    )
    event_id = fields.Int(required=True,load_only=True)
    

# Schema for displaying Selection information in the response
class SelectionSchemaOutput(SelectionSchema):
    
    outcome = EnumStringField(attribute='outcome')
    event_id = fields.Int(dump_only=True)
    event = fields.Nested(EventSchema(only=('id','name','slug' ,'active')), dump_only=True)
    sport_name = fields.String(attribute='event.sport.name', dump_only=True)
    sport_name = fields.String(attribute='event.sport.name', dump_only=True)
    sport_active = fields.Boolean(attribute='event.sport.active', dump_only=True)

# Schema for searching/filtering Selections
class SelectionSearchSchema(Schema):
    name = fields.Str(validate=validate.Length(max=255))
    event_id = fields.Int()
    outcome = fields.Str(validate=validate.OneOf(['UNSETTLED','VOID','LOSE','WIN']))
    active = fields.Bool(validate=validate.OneOf([True, False]))
    price = fields.Decimal(as_string=True, places=2)

# Schema for updating a Selection    
class SelectionUpdateSchema(SelectionSearchSchema):
    event_id = fields.Int(dump_only=True)
    
# Schema for regex filtering       
class RegexFilterSchema(Schema):
    regex_pattern = fields.Str(required=True)





   