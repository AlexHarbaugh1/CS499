import psycopg2
from contextlib import contextmanager
from EncryptionKey import getKeys
import os
import json

# Define the path for storing connection settings
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".HospitalManagementSystem")
CONFIG_FILE = os.path.join(CONFIG_DIR, "connection_config.json")

global_connection = None

def load_connection_params():
    """Load connection parameters from a configuration file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'huntsvillehospital',
            'user': 'postgres',
            'password': '49910'
        }
    except Exception as e:
        print(f"Error loading connection parameters: {e}")
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'huntsvillehospital',
            'user': 'postgres',
            'password': '49910'
        }

@contextmanager
def get_cursor():
    """Context manager for handling database connections."""
    global global_connection
    if global_connection is None or global_connection.closed:
        createConnection()
    cursor = global_connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()

def run():
    """Test connection to the database and verify it exists"""
    # Load connection parameters
    conn_params = load_connection_params()
    
    # Try to connect to the database
    try:
        # First try to connect directly to huntsvillehospital
        conn = psycopg2.connect(
            database='huntsvillehospital',
            user=conn_params['user'],
            password=conn_params['password'],
            host=conn_params['host'],
            port=conn_params['port']
        )
        conn.close()
        print("Successfully connected to huntsvillehospital database")
        return True
    except psycopg2.Error:
        # If that fails, try to connect to the specified database
        try:
            conn = psycopg2.connect(
                database=conn_params['database'],
                user=conn_params['user'],
                password=conn_params['password'],
                host=conn_params['host'],
                port=conn_params['port']
            )
            conn.close()
            print(f"Successfully connected to {conn_params['database']} database")
            return True
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            return False

def createConnection():
    """Create a connection to the database using the saved parameters"""
    global global_connection
    try:
        # Load connection parameters
        conn_params = load_connection_params()
        
        # Connect to the database
        if global_connection is None or global_connection.closed:
            global_connection = psycopg2.connect(
                database=conn_params['database'],
                user=conn_params['user'],
                password=conn_params['password'],
                host=conn_params['host'],
                port=conn_params['port']
            )
            global_connection.autocommit = True
            print("Connection established")
        else:
            print("Using existing connection")
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def userLogin(username, password, fixedSalt):
  with get_cursor() as cursor:
    sql = """SELECT (password_hash = crypt(%s, password_hash)) AS password_match
    FROM Staff WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex');"""
    params = (
        password,
        username, fixedSalt
    )
    cursor.execute(sql, params)
    results = cursor.fetchone()
    if (not results) or (not results[0]):
      print("Incorrect Username or Password")
      
      return False
    else:

      sql = """SELECT EXISTS (SELECT 1 FROM activeuser WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex'));"""
      params = (username, fixedSalt)
      cursor.execute(sql, params)
      if not cursor.fetchone()[0]:  # Fixed this line to access the boolean value
          sql = """SELECT set_config(
                'app.current_user', 
                %s,
                false
              );"""
          params = (
            username,
          )
          cursor.execute(sql, params)
          sql = """SELECT set_config(
                'app.current_user_id', 
                (SELECT user_id::TEXT FROM staff 
                WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex')
                LIMIT 1),
                false
              );"""
          params = (
            username, fixedSalt
          )
          cursor.execute(sql, params)
          
          # Get user ID after setting the config
          sql = """SELECT current_setting('app.current_user_id', true)::INT;"""
          cursor.execute(sql)
          current_user_id = cursor.fetchone()[0]
          
          # Insert both user_id and username_hash
          sql = """INSERT INTO activeuser(user_id, username_hash)
                  VALUES (%s, encode(digest(%s || %s, 'sha256'), 'hex'));"""
          params = (current_user_id, username, fixedSalt)
          cursor.execute(sql, params)
          
          sql = """SELECT set_config(
                'app.current_user_type', 
                (SELECT type_name FROM staff NATURAL JOIN usertype WHERE user_id::TEXT = (SELECT current_setting('app.current_user_id', true))
                LIMIT 1),
                false
              );"""
          cursor.execute(sql)
          usertype = getCurrentUserType()  # Changed to call the function instead
          role = usertype.lower().replace(" ", "") + "_role"
          sql = """SET ROLE %s;"""
          params = (role,)
          cursor.execute(sql, params)
          log_action("Logged In")
          print("Successfully Signed In")
          return True
      else:
          print("User Already Logged In On A Machine")
          return False

def userLogout():
  with get_cursor() as cursor:
    userID = getCurrentUserID()
    username = getCurrentUsername()
    sql = """SELECT set_config(
            'app.current_user', 
            NULL,
            false
          );"""
    cursor.execute(sql)
    sql = """SELECT set_config(
            'app.current_user_id', 
            NULL,
            false
          );"""
    cursor.execute(sql)
    sql = """SELECT set_config(
            'app.current_user_type', 
            NULL,
            false
          );"""
    cursor.execute(sql)
    sql = """SET ROLE administrator_role;"""
    cursor.execute(sql)
    sql = """DELETE FROM activeuser
              WHERE user_id = %s;"""
    params = (userID,)
    cursor.execute(sql, params)
    log_action(f"{username} Logged Out")
    print("User Logged Out")

def getCurrentUserType():
  with get_cursor() as cursor:
    cursor.execute("SELECT current_setting('app.current_user_type', true) AS user_type;")
    results = cursor.fetchone()[0]
    
  return results

def getCurrentUsername():
  with get_cursor() as cursor:
    cursor.execute("SELECT current_setting('app.current_user', true) AS user_type;")
    results = cursor.fetchone()[0]
    
  return results

def getCurrentUserID():
  with get_cursor() as cursor:
    cursor.execute("SELECT current_setting('app.current_user_id', true) AS user_type;")
    results = cursor.fetchone()[0]
    
  return results


# Import this here to avoid circular import
from InsertData import log_action

if __name__ == "__main__":
    run()