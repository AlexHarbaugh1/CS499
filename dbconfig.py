#!/usr/bin/env python
# dbconfig.py - Database Configuration Loader

import os
import sys
import configparser
from pathlib import Path

def get_config_path():
    """Get the path to the configuration file"""
    # Check if running as executable or as script
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(os.path.dirname(sys.executable))
    else:
        # Running as script
        app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    return app_dir / "config.ini"

def load_config():
    """Load database configuration"""
    config_path = get_config_path()
    
    # Default configuration
    db_config = {
        "host": "localhost",
        "port": "5432",
        "user": "postgres",
        "password": "49910",  # Default from the original code
        "database": "huntsvillehospital"
    }
    
    # If config file exists, load values from it
    if config_path.exists():
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if "Database" in config:
            for key in db_config:
                if key in config["Database"]:
                    db_config[key] = config["Database"][key]
    
    return db_config

def save_config(db_config):
    """Save database configuration"""
    config_path = get_config_path()
    
    config = configparser.ConfigParser()
    config["Database"] = db_config
    
    with open(config_path, 'w') as config_file:
        config.write(config_file)

if __name__ == "__main__":
    # Test loading configuration
    config = load_config()
    print("Database Configuration:")
    for key, value in config.items():
        # Mask password for security
        if key == "password":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")