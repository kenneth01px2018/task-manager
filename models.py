from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)        # unique identifier
    title = db.Column(db.String(200), nullable=False)   # required short text
    description = db.Column(db.String(500))             # optional longer text
    completed = db.Column(db.Boolean, default=False)    # boolean flag

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r}>"
