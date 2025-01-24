import logging
from sqlalchemy import inspect, text
from flask import current_app
from flask_migrate import upgrade as flask_migrate_upgrade
from .models import db

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and run migrations if needed."""
    try:
        # Get database connection
        engine = db.engine
        
        # Check if any tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("No tables found in database. Running migrations...")
            # Run all migrations
            flask_migrate_upgrade()
            logger.info("Database migrations completed successfully.")
        else:
            logger.info("Database tables already exist. Checking migrations...")
            # Check if alembic_version table exists
            if 'alembic_version' not in existing_tables:
                logger.warning("Found existing tables but no alembic_version. This might cause issues with future migrations.")
            else:
                # Get current revision
                with engine.connect() as connection:
                    current_rev = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
                    logger.info(f"Current database revision: {current_rev}")
                
                # Run any pending migrations
                flask_migrate_upgrade()
                logger.info("Any pending migrations have been applied.")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
