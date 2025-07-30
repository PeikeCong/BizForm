from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///frameworks.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

# --- Models ---

class Framework(Base):
    __tablename__ = 'frameworks'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    categories = relationship('Category', back_populates='framework')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    framework_id = Column(Integer, ForeignKey('frameworks.id'))
    framework = relationship('Framework', back_populates='categories')

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True)
    input_text = Column(Text)
    framework = Column(String(50))
    result = Column(Text)          # Framework insights
    summary = Column(Text)         # Summary
    suggestions = Column(Text)     # Suggestions
    created_at = Column(DateTime, default=datetime.utcnow)

    feedback = relationship("Feedback", back_populates="session", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("analysis_sessions.id"))
    thumb = Column(String)  # e.g., "👍 Yes" or "👎 No"
    note = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("AnalysisSession", back_populates="feedback")

# Initialize DB (run once)
def init_db():
    Base.metadata.create_all(engine)
