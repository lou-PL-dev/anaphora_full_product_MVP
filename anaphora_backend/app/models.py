"""
ORM models — field names follow PRD section 33 (Suggested Data Objects)
directly, so the schema is traceable back to the spec.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from .database import Base


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
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    signals = relationship("BlueprintSignal", back_populates="user")
    discovery_responses = relationship("DiscoveryResponse", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    messages = Column(JSON, default=list)  # [{"role": "user"|"assistant", "content": "..."}]
    status = Column(String, default="active")  # active | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")


class BlueprintSignal(Base):
    __tablename__ = "blueprint_signals"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"))
    perspective = Column(String)  # "ME" | "IDEAL_PARTNER"
    category = Column(String)     # personality | lifestyle | relationship_dynamic | attraction | values | dealbreakers
    dimension = Column(String, nullable=True)  # e.g. "emotional_expression" (optional, PRD sec 13)
    value = Column(String, nullable=True)      # e.g. "high" (optional, PRD sec 13)
    label = Column(String)        # e.g. "Emotionally expressive"
    strength = Column(String, default="preference")  # hard_requirement | strong_preference | preference | unknown
    source = Column(String)       # "conversation" | "discovery"
    evidence_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="signals")


class Discovery(Base):
    __tablename__ = "discoveries"

    id = Column(String, primary_key=True)  # human-readable slug, e.g. "life_you_are_building"
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
