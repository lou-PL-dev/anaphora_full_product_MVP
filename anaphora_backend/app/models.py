"""
ORM models — field names follow PRD section 33 (Suggested Data Objects)
directly, so the schema is traceable back to the spec.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship

from .database import Base

from pgvector.sqlalchemy import Vector

EMBEDDING_DIM = 1536  # text-embedding-3-small


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    language = Column(String, default="en")
    location = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    gender_preference = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    preferred_age_range = Column(String, nullable=True)  # e.g. "30-40"
    blueprint_narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    signals = relationship("BlueprintSignal", back_populates="user")
    discovery_responses = relationship("DiscoveryResponse", back_populates="user")
    events = relationship("TesterEvent", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    messages = Column(JSON, default=list)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")


class BlueprintSignal(Base):
    __tablename__ = "blueprint_signals"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    perspective = Column(String)
    category = Column(String)
    dimension = Column(String, nullable=True)
    value = Column(String, nullable=True)
    label = Column(String)
    strength = Column(String, default="preference")
    source = Column(String)
    evidence_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="signals")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    photo_url = Column(String, nullable=True)
    narrative = Column(Text)
    signals = Column(JSON)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)


class Discovery(Base):
    __tablename__ = "discoveries"

    id = Column(String, primary_key=True)
    title = Column(String)
    status = Column(String, default="active")


class DiscoveryResponse(Base):
    __tablename__ = "discovery_responses"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    discovery_id = Column(String, ForeignKey("discoveries.id"))
    question_id = Column(String)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="discovery_responses")


class TesterEvent(Base):
    """Small product-research event stream for private MVP testing.

    This is intentionally not a general analytics system: just enough to
    reconstruct a tester journey beside the qualitative conversation data.
    """
    __tablename__ = "tester_events"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    event = Column(String, index=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="events")


class FriendInvite(Base):
    __tablename__ = "friend_invites"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class FriendResponse(Base):
    __tablename__ = "friend_responses"

    id = Column(String, primary_key=True, default=gen_id)
    invite_id = Column(String, ForeignKey("friend_invites.id"))
    friend_name = Column(String)
    raw_answers = Column(JSON)
    narrative = Column(Text, nullable=True)
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invite = relationship("FriendInvite")


class FriendSignal(Base):
    __tablename__ = "friend_signals"

    id = Column(String, primary_key=True, default=gen_id)
    response_id = Column(String, ForeignKey("friend_responses.id"))
    perspective = Column(String)
    category = Column(String)
    label = Column(String)
    strength = Column(String, default="preference")
    evidence_text = Column(Text, nullable=True)
    status = Column(String, default="pending")

    response = relationship("FriendResponse")
