from sqlalchemy.orm import Session
from models.memory_model import Memory

def load_context(db: Session, limit: int = 6):
    rows = (
        db.query(Memory)
        .order_by(Memory.timestamp.asc())
        .limit(limit)
        .all()
    )
    return [{"role": row.role, "content": row.content} for row in rows]

def save_turn(db: Session, role: str, content: str):
    entry = Memory(role=role, content=content)
    db.add(entry)
    db.commit()
