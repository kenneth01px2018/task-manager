import os
from flask import Flask, request, jsonify, url_for
from marshmallow import ValidationError
from models import db, Task
from schemas import task_schema, tasks_schema


def create_app():
    """Application factory: returns a configured Flask app.
       Using a factory makes testing and configuration easier later."""
    app = Flask(__name__)
    # In production, read DATABASE_URL from env var, not hard-coded.
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Create tables for quick prototyping. For real apps use migrations (Flask-Migrate).
    with app.app_context():
        db.create_all()

    # ---- Error handler for validation errors ----
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        # Marshmallow raises ValidationError on bad input; return 400 + details
        return jsonify({"errors": err.messages}), 400

    # ---- Create a task (POST /tasks) ----
    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json() or {}
        # Validate and (optionally) produce a Task instance
        # Here we use schema.load which will raise ValidationError on bad data
        task = task_schema.load(data)
        db.session.add(task)       # add new Task object to session
        db.session.commit()        # persist to DB
        # Location header is nice REST practice: indicates where the resource lives
        return task_schema.jsonify(task), 201, {"Location": url_for("get_task", task_id=task.id)}

    # ---- Get all tasks (GET /tasks) ----
    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        # You might add pagination & filtering here (limit/offset, completed=true)
        all_tasks = Task.query.order_by(Task.id.desc()).all()
        return tasks_schema.jsonify(all_tasks)

    # ---- Get one task (GET /tasks/<id>) ----
    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        return task_schema.jsonify(task)

    # ---- Update a task (PUT /tasks/<id>) ----
    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json() or {}
        # Partial update: allow missing fields (use partial=True)
        updated = task_schema.load(data, instance=task, partial=True)  # merges into instance
        db.session.add(updated)
        db.session.commit()
        return task_schema.jsonify(updated)

    # ---- Delete a task (DELETE /tasks/<id>) ----
    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        db.session.delete(task)
        db.session.commit()
        # 204 No Content is standard for successful DELETE with no body
        return "", 204

    return app


# For local dev you can run: FLASK_APP=app.py flask run
if __name__ == "__main__":
    create_app().run(debug=True)
