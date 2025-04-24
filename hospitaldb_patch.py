#!/usr/bin/env python
# hospitaldb_patch.py - Apply patches to hospitalDB.py

import re
import os
from pathlib import Path

def apply_patches():
    """Apply patches to hospitalDB.py"""
    # The original hospitalDB.py file
    hospital_db_path = Path("hospitalDB.py")
    
    if not hospital_db_path.exists():
        print(f"Error: {hospital_db_path} not found")
        return False
    
    # Read the original file
    with open(hospital_db_path, 'r') as f:
        content = f.read()
    
    # Add import for dbconfig at the top
    import_patch = "import psycopg2\nfrom InsertData import log_action\nfrom contextlib import contextmanager\nfrom EncryptionKey import getKeys\nimport dbconfig\n"
    content = re.sub(r"import psycopg2\nfrom InsertData import log_action\nfrom contextlib import contextmanager\nfrom EncryptionKey import getKeys", import_patch, content)
    
    # Update the createConnection function to use the config
    original_conn_func = r"""def createConnection\(\):
  global global_connection
  if global_connection is None or global_connection.closed:
        global_connection = psycopg2.connect\(
            database="huntsvillehospital",
            user='postgres',
            password='49910',
            host='localhost',
            port='5432'
        \)
        global_connection.autocommit = True"""
    
    new_conn_func = """def createConnection():
  global global_connection
  if global_connection is None or global_connection.closed:
        # Load database configuration
        db_config = dbconfig.load_config()
        
        global_connection = psycopg2.connect(
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        global_connection.autocommit = True"""
    
    content = re.sub(original_conn_func, new_conn_func, content)
    
    # Update the run function to use the config for initial connection
    original_run_conn = r"""  conn = psycopg2.connect\(
    database="postgres",
      user='postgres',
      password='49910',
      host='localhost',
      port= '5432'
  \)"""
    
    new_run_conn = """  # Load database configuration
  db_config = dbconfig.load_config()
  
  conn = psycopg2.connect(
    database="postgres",
      user=db_config["user"],
      password=db_config["password"],
      host=db_config["host"],
      port=db_config["port"]
  )"""
    
    content = re.sub(original_run_conn, new_run_conn, content)
    
    # Backup the original file
    backup_path = hospital_db_path.with_suffix('.py.bak')
    os.rename(hospital_db_path, backup_path)
    
    # Write the modified content
    with open(hospital_db_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully patched {hospital_db_path}")
    print(f"Original file backed up to {backup_path}")
    
    return True

if __name__ == "__main__":
    apply_patches()