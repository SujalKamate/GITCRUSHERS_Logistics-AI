"""
Database setup and initialization script.
Run this to create the PostgreSQL database and tables.
"""
import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database_models_example import Base, DatabaseService
from config.settings import settings

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/logistics_ai")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engines
sync_engine = create_engine(DATABASE_URL, poolclass=NullPool)
async_engine = create_async_engine(ASYNC_DATABASE_URL, poolclass=NullPool)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def create_database():
    """Create database if it doesn't exist."""
    # Connect to postgres database to create our database
    postgres_url = DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    postgres_engine = create_engine(postgres_url, poolclass=NullPool)
    
    db_name = DATABASE_URL.split('/')[-1]
    
    with postgres_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        if not result.fetchone():
            # Create database
            conn.execute(text("COMMIT"))  # End any transaction
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Created database: {db_name}")
        else:
            print(f"Database {db_name} already exists")
    
    postgres_engine.dispose()


async def create_tables():
    """Create all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Created all tables")


async def init_database():
    """Initialize the database with tables."""
    await create_database()
    await create_tables()
    print("Database initialization complete")


def get_db():
    """Get database session (sync)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        yield session


def get_database_service():
    """Get database service instance."""
    db = SessionLocal()
    return DatabaseService(db)


if __name__ == "__main__":
    asyncio.run(init_database())