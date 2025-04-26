#!/usr/bin/env python
# db_migration.py - Database Migration Script (Updated for folder structure)

import os
import sys
import logging
import subprocess
import psycopg2
from pathlib import Path
import time
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hospital_migration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DatabaseMigration")

# Function to import a module from a specific path
def import_module_from_path(module_name, module_path):
    """Import a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        logger.error(f"Module {module_name} not found at {module_path}")
        return None
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import config handler from current directory
try:
    from config_handler import get_config_handler
except ImportError:
    config_handler_path = os.path.join(os.path.dirname(__file__), "config_handler.py")
    if os.path.exists(config_handler_path):
        config_handler_module = import_module_from_path("config_handler", config_handler_path)
        get_config_handler = config_handler_module.get_config_handler
    else:
        logger.error("config_handler.py not found")
        sys.exit(1)

class DatabaseMigration:
    """Handles database migrations for the Hospital Management System"""
    
    def __init__(self):
        """Initialize the database migration"""
        self.config = get_config_handler()
        self.db_config = self.config.get_db_config()
        
        # Determine the application directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = Path(os.path.dirname(sys.executable))
        else:
            # Running as script
            self.app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Look for the hospitalDB module in several possible locations
        self.hospitalDB_module = None
        possible_paths = [
            os.path.join(self.app_dir, "hospitalDB.py"),
            os.path.join(self.app_dir, "DatabaseHost", "hospitalDB.py")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found hospitalDB.py at {path}")
                self.hospitalDB_module = import_module_from_path("hospitalDB", path)
                break
        
        if not self.hospitalDB_module:
            logger.error("hospitalDB.py not found in any expected location")
        
        # SQL scripts directory
        self.sql_dir = self.app_dir / "sql"
        self.sql_dir.mkdir(parents=True, exist_ok=True)
    
    def check_postgres_connection(self):
        """Check if PostgreSQL is running and accessible"""
        logger.info("Checking PostgreSQL connection...")
        
        try:
            # Connect to postgres database (default database)
            conn = psycopg2.connect(
                database="postgres",
                user=self.db_config["user"],
                password=self.db_config["password"],
                host=self.db_config["host"],
                port=self.db_config["port"]
            )
            conn.close()
            logger.info("Successfully connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
    
    def check_database_exists(self):
        """Check if the hospital database exists"""
        logger.info(f"Checking if database '{self.db_config['database']}' exists...")
        
        try:
            # Connect to postgres database (default database)
            conn = psycopg2.connect(
                database="postgres",
                user=self.db_config["user"],
                password=self.db_config["password"],
                host=self.db_config["host"],
                port=self.db_config["port"]
            )
            conn.autocommit = True
            
            # Create a cursor
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(f"SELECT EXISTS (SELECT datname FROM pg_catalog.pg_database WHERE datname='{self.db_config['database']}');")
            exists = cursor.fetchone()[0]
            
            # Close connections
            cursor.close()
            conn.close()
            
            logger.info(f"Database '{self.db_config['database']}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking if database exists: {e}")
            return False
    
    def create_database(self):
        """Create the hospital database"""
        logger.info(f"Creating database '{self.db_config['database']}'...")
        
        try:
            # Connect to postgres database (default database)
            conn = psycopg2.connect(
                database="postgres",
                user=self.db_config["user"],
                password=self.db_config["password"],
                host=self.db_config["host"],
                port=self.db_config["port"]
            )
            conn.autocommit = True
            
            # Create a cursor
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE {self.db_config['database']};")
            
            # Close connections
            cursor.close()
            conn.close()
            
            logger.info(f"Database '{self.db_config['database']}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def run_migration(self):
        """Run the database migration"""
        logger.info("Starting database migration...")
        
        # Check PostgreSQL connection
        if not self.check_postgres_connection():
            logger.error("Failed to connect to PostgreSQL")
            return False
        
        # Check if database exists
        if not self.check_database_exists():
            # Create database
            if not self.create_database():
                logger.error("Failed to create database")
                return False
        
        # Initialize the database
        logger.info("Initializing database...")
        
        # Use the imported hospitalDB module
        if self.hospitalDB_module:
            try:
                # Run the database initialization
                self.hospitalDB_module.run()
                
                logger.info("Database initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                return False
        else:
            logger.error("hospitalDB module not available")
            return False
    
    def start_postgres_service(self):
        """Start the PostgreSQL service if it's not running"""
        logger.info("Attempting to start PostgreSQL service...")
        
        try:
            if sys.platform == "win32":
                # Windows
                subprocess.run(["net", "start", "postgresql-x64-14"], check=False)
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["brew", "services", "start", "postgresql"], check=False)
            else:
                # Linux
                subprocess.run(["sudo", "systemctl", "start", "postgresql"], check=False)
            
            # Wait for the service to start
            time.sleep(5)
            
            logger.info("PostgreSQL service started")
            return True
        except Exception as e:
            logger.error(f"Error starting PostgreSQL service: {e}")
            return False
    
    def run_with_retry(self, max_retries=3):
        """Run the migration with retry logic"""
        for attempt in range(max_retries):
            logger.info(f"Migration attempt {attempt + 1}/{max_retries}")
            
            # Check PostgreSQL connection
            if not self.check_postgres_connection():
                # Try to start the service
                self.start_postgres_service()
                
                # Wait for the service to start
                time.sleep(5)
                
                # Check connection again
                if not self.check_postgres_connection():
                    logger.error("Still unable to connect to PostgreSQL")
                    continue
            
            # Run the migration
            if self.run_migration():
                logger.info("Migration completed successfully")
                return True
            
            # Wait before retrying
            time.sleep(2)
        
        logger.error(f"Migration failed after {max_retries} attempts")
        return False

def run_migration():
    """Run the database migration"""
    migration = DatabaseMigration()
    return migration.run_with_retry()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)