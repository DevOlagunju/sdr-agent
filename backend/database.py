from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=True,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    company_domain = Column(String, unique=True, index=True)
    company_name = Column(String)
    industry = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    research_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="draft")  # draft, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
