from datetime import datetime, timezone

from app import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # "user", "assistant" veya "system"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Message {self.id} - {self.role}: {self.content}>"
