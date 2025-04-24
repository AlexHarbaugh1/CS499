#!/usr/bin/env python
# config_handler.py - Application Configuration Handler

import os
import sys
import json
import configparser
from pathlib import Path
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hospital_system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ConfigHandler")

class ConfigHandler:
    """Handles configuration for the Hospital Management System"""
    
    def __init__(self):
        """Initialize the configuration handler"""
        # Determine the application directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = Path(os.path.dirname(sys.executable))
        else:
            # Running as script
            self.app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Configuration file paths
        self.config_path = self.app_dir / "config.ini"
        self.hcp_config_path = Path.home() / ".config" / "hcp"
        
        # Default configuration
        self.config = configparser.ConfigParser()
        
        # Load or create configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration from file, or create default if it doesn't exist"""
        if self.config_path.exists():
            try:
                self.config.read(self.config_path)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                self.create_default_config()
        else:
            logger.info("Configuration file not found, creating default")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        # Database section
        if "Database" not in self.config:
            self.config["Database"] = {}
        
        # Set default values if not present
        if "host" not in self.config["Database"]:
            self.config["Database"]["host"] = "localhost"
        if "port" not in self.config["Database"]:
            self.config["Database"]["port"] = "5432"
        if "user" not in self.config["Database"]:
            self.config["Database"]["user"] = "postgres"
        if "password" not in self.config["Database"]:
            self.config["Database"]["password"] = "49910"
        if "database" not in self.config["Database"]:
            self.config["Database"]["database"] = "huntsvillehospital"
        
        # Application section
        if "Application" not in self.config:
            self.config["Application"] = {}
        
        # Set default values if not present
        if "log_level" not in self.config["Application"]:
            self.config["Application"]["log_level"] = "INFO"
        if "data_directory" not in self.config["Application"]:
            self.config["Application"]["data_directory"] = str(self.app_dir / "data")
        
        # HCP section (if configured)
        if "HCP" not in self.config and self.hcp_config_path.exists():
            self.config["HCP"] = {}
            
            # Try to read HCP configuration
            credentials_path = self.hcp_config_path / "credentials.hcl"
            config_path = self.hcp_config_path / "config.hcl"
            
            if credentials_path.exists() and config_path.exists():
                # Set HCP configured flag
                self.config["HCP"]["configured"] = "true"
            else:
                self.config["HCP"]["configured"] = "false"
        
        # Save the configuration
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_db_config(self):
        """Get database configuration"""
        return {
            "host": self.config["Database"].get("host", "localhost"),
            "port": self.config["Database"].get("port", "5432"),
            "user": self.config["Database"].get("user", "postgres"),
            "password": self.config["Database"].get("password", "49910"),
            "database": self.config["Database"].get("database", "huntsvillehospital")
        }
    
    def update_db_config(self, host=None, port=None, user=None, password=None, database=None):
        """Update database configuration"""
        if host:
            self.config["Database"]["host"] = host
        if port:
            self.config["Database"]["port"] = port
        if user:
            self.config["Database"]["user"] = user
        if password:
            self.config["Database"]["password"] = password
        if database:
            self.config["Database"]["database"] = database
        
        return self.save_config()
    
    def get_app_config(self):
        """Get application configuration"""
        return {
            "log_level": self.config["Application"].get("log_level", "INFO"),
            "data_directory": self.config["Application"].get("data_directory", str(self.app_dir / "data"))
        }
    
    def is_hcp_configured(self):
        """Check if HCP is configured"""
        if "HCP" not in self.config:
            return False
        
        return self.config["HCP"].getboolean("configured", False)
    
    def create_database_backup(self, backup_path=None):
        """Create a database backup using pg_dump"""
        db_config = self.get_db_config()
        
        # Set default backup path if not provided
        if not backup_path:
            data_dir = Path(self.get_app_config()["data_directory"])
            data_dir.mkdir(parents=True, exist_ok=True)
            backup_path = data_dir / f"{db_config['database']}_backup.sql"
        
        try:
            # Build the pg_dump command
            cmd = [
                "pg_dump",
                "-h", db_config["host"],
                "-p", db_config["port"],
                "-U", db_config["user"],
                "-F", "c",  # Custom format (compressed)
                "-b",  # Include large objects
                "-v",  # Verbose
                "-f", str(backup_path),
                db_config["database"]
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]
            
            # Run pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created successfully at {backup_path}")
                return True, str(backup_path)
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return False, result.stderr
        
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False, str(e)
    
    def restore_database_backup(self, backup_path):
        """Restore a database backup using pg_restore"""
        db_config = self.get_db_config()
        
        try:
            # Build the pg_restore command
            cmd = [
                "pg_restore",
                "-h", db_config["host"],
                "-p", db_config["port"],
                "-U", db_config["user"],
                "-d", db_config["database"],
                "-c",  # Clean (drop) database objects before recreating
                "-v",  # Verbose
                str(backup_path)
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]
            
            # Run pg_restore
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database restored successfully from {backup_path}")
                return True, "Database restored successfully"
            else:
                logger.error(f"Database restore failed: {result.stderr}")
                return False, result.stderr
        
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False, str(e)

# Singleton instance
_config_handler = None

def get_config_handler():
    """Get the singleton ConfigHandler instance"""
    global _config_handler
    if _config_handler is None:
        _config_handler = ConfigHandler()
    return _config_handler

if __name__ == "__main__":
    # Test the configuration handler
    config = get_config_handler()
    print("Database Configuration:")
    db_config = config.get_db_config()
    for key, value in db_config.items():
        if key == "password":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    
    print("\nApplication Configuration:")
    app_config = config.get_app_config()
    for key, value in app_config.items():
        print(f"  {key}: {value}")
    
    print(f"\nHCP Configured: {config.is_hcp_configured()}")