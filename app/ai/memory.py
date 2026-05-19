from app.models import Message
from app import db


def save_message(user_id, role, content):
    """Yeni bir mesajı veritabanına kaydeder."""
    message = Message(user_id=user_id, role=role, content=content)
    db.session.add(message)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def get_chat_history(user_id, limit=10):
    """Belirli bir kullanıcı için son N mesajı getirir."""
    messages = (
        Message.query.filter_by(user_id=user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]


def clear_chat_history(user_id):
    """Belirli bir kullanıcının tüm geçmişini siler."""
    try:
        Message.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
