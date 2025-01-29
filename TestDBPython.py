
import psycopg2
def run():
  # Connect to root database in postgres
  # This lets you create another database within postgres
  conn = psycopg2.connect(
    database="postgres",
      user='postgres',
      password='49910',
      host='localhost',
      port= '5432'
  )
  # Autocommit makes all SQL commands commit immediately after execution
  # Without it you would call cursor.commit() after execution to commit the command to the database 
  conn.autocommit = True
  
  # Create a cursor
  # Cursors are used to pass SQL statements to a database and manipulate it
  # Select statements store the result of the statement within the cursor
  # The results can be accessed through cursor.fetchall() for all results or cursor.fetchone() for the first result
  cursor = conn.cursor()

  # Check the current list of databases withing the root database
  # If huntsvillehospital already exists the code finishes
  # If huntsvillehospital does not exist it creates the database and all tables that are within it
  cursor.execute("""SELECT EXISTS 
                (SELECT datname FROM pg_catalog.pg_database
                WHERE datname='huntsvillehospital')""")
  # Exists returns true or false if the SQL statement passed returns a result
  if(not cursor.fetchone()[0]):
    cursor.execute("""CREATE DATABASE huntsvillehospital""")
    # After creating the new database create a new connection to access it
    con2 = psycopg2.connect(
      database="huntsvillehospital",
      user='postgres',
      password='49910',
      host='localhost',
      port= '5432'
    )

    con2.autocommit = True
    cursor2 = con2.cursor()
    cursor2.execute("CREATE EXTENSION pgcrypto;")
    # Pass CREATE TABLE statements to populate the database.
    cursor2.execute("""CREATE TABLE Users (id serial PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                firstname VARCHAR(255) NOT NULL,
                lastname VARCHAR(255) NOT NULL,
                type VARCHAR(255) CHECK (type IN ('Physician', 'Office Staff', 'Volunteer', 'Medical Personnel')) NOT NULL);"""
                )
    cursor2.execute("""CREATE TABLE Patients (id serial PRIMARY KEY,
                lastname VARCHAR(255) NOT NULL,
                firstname VARCHAR(255) NOT NULL,
                middlename VARCHAR(255),
                mailing_address VARCHAR(255),
                home_phone VARCHAR(10),
                work_phone VARCHAR(10),
                contact1_name VARCHAR(255),
                contact1_phone VARCHAR(10),
                contact2_name VARCHAR(255),
                contact2_phone VARCHAR(10),
                family_doctor VARCHAR(255),
                insurance_carrier VARCHAR(255),
                insurance_account VARCHAR(255),
                insurance_group_number VARCHAR(255),
                billing_information TEXT,
                amount_paid VARCHAR(12),
                amount_owed VARCHAR(12),
                amount_paid_insurance VARCHAR(12)      
                );"""
                )
    cursor2.execute("""CREATE TABLE Prescriptions (id serial PRIMARY KEY,
                name VARCHAR(255),
                amount VARCHAR(255),
                schedule VARCHAR(255),
                procedures text,
                notes text      
                );"""
                )
    cursor2.execute("""CREATE TABLE Admissions (id serial PRIMARY KEY,
                patientID int REFERENCES Patients(id),
                time_of_admission timestamp NOT NULL,
                reason_for_admission VARCHAR(255),
                personnelID int REFERENCES Users(id),
                facility VARCHAR(50),
                floor VARCHAR(10),
                room_num int,
                bed_num int,
                time_of_discharge timestamp,
                notes text,
                prescriptionID int REFERENCES Prescriptions(id)    
                );"""
                )
    # Close second connections
    con2.close()
    cursor2.close()
    print("Database Created")
  else:
    print("Database Already Exists")

  # Close first connections
  cursor.close()
  conn.close()
