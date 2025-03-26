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
    # 1. UserType
    cursor2.execute("""CREATE TABLE UserType
                    (type_id SERIAL PRIMARY KEY,
                    type_name VARCHAR(50) NOT NULL UNIQUE);"""
                    )
    # 2. Staff
    cursor2.execute("""CREATE TABLE Staff
                    (user_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    type_id INT NOT NULL REFERENCES UserType(type_id));"""
                    )
    # 3. Patient
    cursor2.execute("""CREATE TABLE Patient
                    (patient_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    middle_name VARCHAR(50),
                    mailing_address TEXT NOT NULL,
                    family_doctor_id INT REFERENCES Staff(user_id));"""
                    )
    # 4. Insurance
    cursor2.execute("""CREATE TABLE Insurance
                    (insurance_id SERIAL PRIMARY KEY,
                    patient_id INT UNIQUE NOT NULL REFERENCES Patient(patient_id),
                    carrier_name VARCHAR(100) NOT NULL,
                    account_number VARCHAR(100) NOT NULL,
                    group_number VARCHAR(100) NOT NULL);"""
                    )
    # 5. Phonenumber
    cursor2.execute("""CREATE TABLE PhoneNumber
                    (patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    phone_type VARCHAR(20) NOT NULL CHECK (phone_type IN ('Home', 'Work', 'Mobile')),
                    phone_number VARCHAR(20) NOT NULL,
                    PRIMARY KEY (patient_id, phone_type));"""
                    )
    # 6. EmergencyContact
    cursor2.execute("""CREATE TABLE EmergencyContact
                    (contact_id SERIAL PRIMARY KEY,
                    patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    contact_name VARCHAR(100) NOT NULL,
                    contact_phone VARCHAR(20) NOT NULL,
                    contact_order INT NOT NULL CHECK (contact_order IN (1, 2)),
                    UNIQUE (patient_id, contact_order));"""
                    )
    # 7. Location
    cursor2.execute("""CREATE TABLE Location
                    (location_id SERIAL PRIMARY KEY,
                    facility VARCHAR(100) NOT NULL,
                    floor INT,
                    room_number VARCHAR(20),
                    bed_number VARCHAR(20));"""
                    )
    # 8. Admission
    cursor2.execute("""CREATE TABLE Admission
                    (admission_id SERIAL PRIMARY KEY,
                    patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    location_id INT NOT NULL REFERENCES Location(location_id),
                    admittance_datetime TIMESTAMP NOT NULL,
                    discharge_datetime TIMESTAMP,
                    reason_for_admission TEXT NOT NULL);"""
                    )
    # 9. Prescription
    cursor2.execute("""CREATE TABLE Prescription
                    (prescription_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    medication_name VARCHAR(100) NOT NULL,
                    amount VARCHAR(50) NOT NULL,
                    schedule TEXT NOT NULL);"""
                    )
    # 10. PatientNote
    cursor2.execute("""CREATE TABLE PatientNote
                    (note_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    author_id INT NOT NULL REFERENCES Staff(user_id),
                    note_type VARCHAR(20) NOT NULL CHECK (note_type IN ('Doctor', 'Nurse')),
                    note_text TEXT NOT NULL,
                    note_datetime TIMESTAMP NOT NULL);"""
                    )
    # 11. ScheduledProcedure
    cursor2.execute("""CREATE TABLE ScheduledProcedure
                    (procedure_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    procedure_name VARCHAR(100) NOT NULL,
                    scheduled_datetime TIMESTAMP NOT NULL);"""
                    )
    # 12. Billing
    cursor2.execute("""CREATE TABLE Billing
                    (billing_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    total_amount_owed DECIMAL(10, 2) NOT NULL,
                    total_amount_paid DECIMAL(10, 2) NOT NULL,
                    insurance_paid DECIMAL(10, 2) NOT NULL);"""
                    )
    # 13. Billing Detail
    cursor2.execute("""CREATE TABLE BillingDetail
                    (billing_detail_id SERIAL PRIMARY KEY,
                    billing_id INT NOT NULL REFERENCES Billing(billing_id),
                    item_description TEXT NOT NULL,
                    charge_amount DECIMAL(10, 2) NOT NULL);"""
                    )
    # Adding Index to Patient table to allow for faster queries on patien names.
    cursor2.execute("CREATE INDEX idx_patient_last_first_name ON Patient (last_name, first_name);")
    cursor2.execute("CREATE INDEX idx_patient_first_name ON Patient (first_name);")

    #Insert User types into database
    cursor2.execute("""INSERT INTO UserType (type_name)
                    VALUES
                    ('Administrator'),
                    ('Medical Personnel'),
                    ('Office Staff'),
                    ('Volunteer'),
                    ('Physician');""")
    
    # Close second connections
    con2.close()
    cursor2.close()
    print("Database Created")
  else:
    print("Database Already Exists")

  # Close first connections
  cursor.close()
  conn.close()
