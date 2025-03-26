import psycopg2
from dotenv import load_dotenv
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
    con2 = getConnection()
    cursor2 = con2.cursor()
    cursor2.execute("CREATE EXTENSION pgcrypto;")
    cursor2.execute("CREATE EXTENSION pg_trgm;")
    # Pass CREATE TABLE statements to populate the database.
    # 1. UserType
    cursor2.execute("""CREATE TABLE UserType
                    (type_id SERIAL PRIMARY KEY,
                    type_name VARCHAR(50) NOT NULL UNIQUE);"""
                    )
    # 2. Staff
    cursor2.execute("""CREATE TABLE Staff
                    (user_id SERIAL PRIMARY KEY,
                    type_id INT NOT NULL REFERENCES UserType(type_id),
                    first_name BYTEA NOT NULL,
                    last_name BYTEA NOT NULL,
                    first_name_prefix_trgms TEXT[],
                    last_name_prefix_trgms TEXT[],
                    username_hash TEXT NOT NULL,
                    username BYTEA NOT NULL,
                    password_hash TEXT NOT NULL);"""
                    )
    # 3. Patient
    cursor2.execute("""CREATE TABLE Patient
                    (patient_id SERIAL PRIMARY KEY,
                    first_name BYTEA NOT NULL,
                    middle_name BYTEA,
                    last_name BYTEA NOT NULL,
                    first_name_prefix_trgms TEXT[],
                    middle_name_prefix_trgms TEXT[],
                    last_name_prefix_trgms TEXT[],
                    mailing_address BYTEA,
                    family_doctor_id INT REFERENCES Staff(user_id));"""
                    )
    # 4. Insurance
    cursor2.execute("""CREATE TABLE Insurance
                    (insurance_id SERIAL PRIMARY KEY,
                    patient_id INT UNIQUE NOT NULL REFERENCES Patient(patient_id),
                    carrier_name BYTEA,
                    account_number BYTEA,
                    group_number BYTEA);"""
                    )
    # 5. Phonenumber
    cursor2.execute("""CREATE TABLE PhoneNumber
                    (patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    phone_type VARCHAR(20) NOT NULL CHECK (phone_type IN ('Home', 'Work', 'Mobile')),
                    phone_number BYTEA,
                    PRIMARY KEY (patient_id, phone_type));"""
                    )
    # 6. EmergencyContact
    cursor2.execute("""CREATE TABLE EmergencyContact
                    (contact_id SERIAL PRIMARY KEY,
                    patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    contact_name BYTEA,
                    contact_phone BYTEA,
                    contact_order INT NOT NULL CHECK (contact_order IN (1, 2)),
                    UNIQUE (patient_id, contact_order));"""
                    )
    # 7. Location
    cursor2.execute("""CREATE TABLE Location
                    (location_id SERIAL PRIMARY KEY,
                    facility VARCHAR(100) NOT NULL,
                    floor INT,
                    room_number VARCHAR(20),
                    bed_number VARCHAR(20),
                    CONSTRAINT unique_location UNIQUE(facility, floor, room_number, bed_number));"""
                    )
    # 8. Admission
    cursor2.execute("""CREATE TABLE Admission(
                    admission_id SERIAL PRIMARY KEY,
                    patient_id INT NOT NULL REFERENCES Patient(patient_id),
                    location_id INT NOT NULL REFERENCES Location(location_id),
                    doctor_id INT NOT NULL REFERENCES Staff(user_id),
                    admittance_datetime BYTEA NOT NULL,
                    discharge_datetime BYTEA,
                    reason_for_admission BYTEA NOT NULL);"""
                    )
    # 9. Approved Visitors
    cursor2.execute("""CREATE TABLE ApprovedVisitor
                    (visitor_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    name BYTEA);""")
    # 10. Prescription
    cursor2.execute("""CREATE TABLE Prescription(
                    prescription_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    medication_name BYTEA NOT NULL,
                    amount BYTEA NOT NULL,
                    schedule BYTEA NOT NULL);"""
                    )
    # 11. PatientNote
    cursor2.execute("""CREATE TABLE PatientNote
                    (note_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    author_id INT NOT NULL REFERENCES Staff(user_id),
                    note_type VARCHAR(20) NOT NULL CHECK (note_type IN ('Doctor', 'Nurse')),
                    note_text BYTEA NOT NULL,
                    note_datetime BYTEA NOT NULL);"""
                    )
    # 12. ScheduledProcedure
    cursor2.execute("""CREATE TABLE ScheduledProcedure
                    (procedure_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    procedure_name BYTEA NOT NULL,
                    scheduled_datetime BYTEA NOT NULL);"""
                    )
    # 13. Billing
    cursor2.execute("""CREATE TABLE Billing
                    (billing_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    total_amount_owed DECIMAL(10, 2) NOT NULL,
                    total_amount_paid DECIMAL(10, 2) NOT NULL,
                    insurance_paid DECIMAL(10, 2) NOT NULL);"""
                    )
    # 14. Billing Detail
    cursor2.execute("""CREATE TABLE BillingDetail
                    (billing_detail_id SERIAL PRIMARY KEY,
                    billing_id INT NOT NULL REFERENCES Billing(billing_id),
                    item_description TEXT NOT NULL,
                    charge_amount DECIMAL(10, 2) NOT NULL);"""
                    )
    # Adding Indexes for Faster Searching and Partial Searching.
    cursor2.execute("CREATE INDEX idx_staff_username_hash ON Staff USING HASH (username_hash);")
    cursor2.execute("CREATE INDEX idx_staff_first_name_prefix_trgms ON Staff USING gin (first_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_staff_last_name_prefix_trgms ON Staff USING gin (last_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_first_name_prefix_trgms ON Patient USING gin (first_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_middle_name_prefix_trgms ON Patient USING gin (middle_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_last_name_prefix_trgms ON Patient USING gin (last_name_prefix_trgms);")
    # Create roles for each user
    # Check if the roles already exist
    cursor2.execute("SELECT rolname from pg_roles;")
    roleslists = cursor2.fetchall()
    roles = []
    for role in roleslists:
      roles.append(role[0])
    if not ('volunteer_role' in roles):
      cursor2.execute("CREATE ROLE volunteer_role;")
      print("Created Volunteer Role!")
    else: print('volunteer_role Already Exists!')
    if not ('medicalpersonel_role' in roles):
      cursor2.execute("CREATE ROLE medicalpersonel_role;")
      print("Created Medical Personel Role!")
    else: print('medicalpersonel_role Already Exists!')
    if not ('administrator_role' in roles):
      cursor2.execute("CREATE ROLE administrator_role;")
      print("Created Administrator Role!")
    else: print('administrator_role Already Exists!')
    if not ('officestaff_role' in roles):
      cursor2.execute("CREATE ROLE officestaff_role;")
      print("Created Office Staff Role!")
    else: print('officestaff_role Already Exists!')
    if not ('physician_role' in roles):
      cursor2.execute("CREATE ROLE physician_role;")
      print("Created Physician Role!")
    else: print('physician_role Already Exists!')
    #Insert User types into database
    cursor2.execute("""INSERT INTO UserType (type_name)
                    VALUES
                    ('Administrator'),
                    ('Medical Personnel'),
                    ('Office Staff'),
                    ('Volunteer'),
                    ('Physician');""")
    # Create Views for data security
    cursor2.execute("""CREATE VIEW SearchView AS
                    SELECT
                    patient_id,
                    first_name,
                    middle_name,
                    last_name,
                    first_name_prefix_trgms,
                    middle_name_prefix_trgms,
                    last_name_prefix_trgms
                    FROM patient"""
                    )
    cursor2.execute("GRANT SELECT ON SearchView TO volunteer_role;")
    cursor2.execute("GRANT SELECT ON SearchView TO officestaff_role;")
    cursor2.execute("GRANT SELECT ON SearchView TO medicalpersonel_role;")
    cursor2.execute("GRANT SELECT ON SearchView TO administrator_role;")
    cursor2.execute("GRANT SELECT ON SearchView TO physician_role;")
    cursor2.execute("""CREATE VIEW VolunteerView AS
                    SELECT
                    p.patient_id,
                    p.first_name,
                    p.last_name,
                    l.facility,
                    l.floor,
                    l.room_number,
                    l.bed_number
                    FROM patient p
                    JOIN admission a ON p.patient_id = a.patient_id
                    JOIN Location l ON a.location_id = l.location_id;""")
    cursor2.execute("""CREATE VIEW officestaff_role AS
                    SELECT""")
    cursor2.execute("GRANT SELECT ON VolunteerView TO volunteer_role;")

    # Close second connections
    con2.commit()
    cursor2.close()
    con2.close()
    print("Database Created")
  else:
    print("Database Already Exists")

  # Close first connections
  cursor.close()
  conn.close()
def getConnection():
  conn = psycopg2.connect(
      database="huntsvillehospital",
      user='postgres',
      password='49910',
      host='localhost',
      port= '5432'
    )
  return conn

if __name__ == "__main__":
  run()