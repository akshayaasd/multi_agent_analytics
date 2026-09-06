from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

class CallRecord(Base):
    __tablename__ = 'call_records'

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime)
    duration = Column(Float)
    disposition = Column(String)
    intent = Column(String)
    confidence = Column(Float)
    fallback_count = Column(Integer)

class EmailDeliveryLog(Base):
    __tablename__ = 'email_delivery_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_status = Column(String)
    timestamp = Column(DateTime)
    recipient = Column(String)
    error_message = Column(String, nullable=True)

# Database connection configuration
DB_TYPE = os.getenv("DB_TYPE", "postgres")

if DB_TYPE == "postgres":
    DB_USER = os.getenv("DB_USER", os.getenv("USER", "postgres"))
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ivr_analytics")
    
    auth_part = f"{DB_USER}:{DB_PASS}" if DB_PASS else DB_USER
    default_url = f"postgresql://{auth_part}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URL = os.getenv("DATABASE_URL", default_url)
else:
    DATABASE_URL = os.getenv("DATABASE_URL", 'sqlite:///ivr_analytics.db')

try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
except Exception as e:
    print(f"Failed to connect to database ({DATABASE_URL}): {e}")
    # Fallback to sqlite if postgres fails for dev purposes, or just let it fail.
    engine = create_engine('sqlite:///ivr_analytics.db')
    Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
