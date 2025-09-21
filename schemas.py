from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Task


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True   # optional: create model instances when loading

    # override/add fields for validation (title must be present)
    title = fields.String(required=True)
    description = fields.String(required=False, allow_none=True)
    completed = fields.Boolean(required=False)


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
