import psycopg2
from EncryptionKey import getKeys
def run():
  keys = getKeys()
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
    con2.autocommit = True
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
    cursor2.execute("""CREATE TABLE ApprovedVisitors
                    (visitors_id SERIAL PRIMARY KEY,
                    admission_id INT NOT NULL REFERENCES Admission(admission_id),
                    names BYTEA[]);""")
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
    # 15. Audit Log
    cursor2.execute("""CREATE TABLE audit_log
                    (username TEXT,
                    action TEXT,
                    timestamp TIMESTAMP);""")
    # Adding Indexes for Faster Searching and Partial Searching.
    cursor2.execute("CREATE INDEX idx_staff_username_hash ON Staff USING HASH (username_hash);")
    cursor2.execute("CREATE INDEX idx_staff_first_name_prefix_trgms ON Staff USING gin (first_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_staff_last_name_prefix_trgms ON Staff USING gin (last_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_first_name_prefix_trgms ON Patient USING gin (first_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_middle_name_prefix_trgms ON Patient USING gin (middle_name_prefix_trgms);")
    cursor2.execute("CREATE INDEX idx_last_name_prefix_trgms ON Patient USING gin (last_name_prefix_trgms);")
    #Insert User types into database
    cursor2.execute("""INSERT INTO UserType (type_name)
                    VALUES
                    ('Administrator'),
                    ('Medical Personnel'),
                    ('Office Staff'),
                    ('Volunteer'),
                    ('Physician');""")
    
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
    if not ('admin_role' in roles):
      cursor2.execute("CREATE ROLE admin_role;")
      print("Created Admin Role!")
    else: print('admin_role Already Exists!')
    if not ('officestaff_role' in roles):
      cursor2.execute("CREATE ROLE officestaff_role;")
      print("Created Office Staff Role!")
    else: print('officestaff_role Already Exists!')
    if not ('physician_role' in roles):
      cursor2.execute("CREATE ROLE physician_role;")
      print("Created Physician Role!")
    else: print('physician_role Already Exists!')
    cursor2.execute("""GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;""")

    # Create Views for data security
    # searchview is the table used for the search screen, accesible to all user roles
    sql = """CREATE VIEW searchview AS
                    SELECT
                    patient_id,
                    pgp_sym_decrypt(first_name, %s) AS first_name,
                    pgp_sym_decrypt(middle_name, %s) AS middle_name,
                    pgp_sym_decrypt(last_name, %s) AS last_name,
                    first_name_prefix_trgms,
                    middle_name_prefix_trgms,
                    last_name_prefix_trgms
                    FROM patient;"""
    params = (
      keys[0],
      keys[0],
      keys[0]
    )
    cursor2.execute(sql, params)
    cursor2.execute("GRANT SELECT ON searchview TO volunteer_role;")
    cursor2.execute("GRANT SELECT ON searchview TO officestaff_role;")
    cursor2.execute("GRANT SELECT ON searchview TO medicalpersonel_role;")
    cursor2.execute("GRANT SELECT ON searchview TO physician_role;")
    # volunteerview selects only the patients name and location as per requirements
    sql = """CREATE VIEW volunteerview AS
                    SELECT
                    p.patient_id,
                    pgp_sym_decrypt(p.first_name, %s) AS first_name,
                    pgp_sym_decrypt(p.middle_name, %s) AS middle_name,
                    pgp_sym_decrypt(p.last_name, %s) AS last_name,
                    l.facility,
                    l.floor,
                    l.room_number,
                    l.bed_number,
                    ARRAY (SELECT pgp_sym_decrypt(visitor, %s)
                    FROM unnest(v.names) AS visitor) AS decrypted_visitors
                    FROM patient p
                    JOIN admission a ON p.patient_id = a.patient_id
                    JOIN Location l ON a.location_id = l.location_id
                    JOIN approvedvisitors v on a.admission_id = v.admission_id
                    WHERE a.discharge_datetime IS NULL;"""
    params = (keys[0],)*4
    cursor2.execute(sql, params)
    cursor2.execute("GRANT SELECT ON volunteerview TO volunteer_role;")
    # Office View Selects all none medical data and uses triggers to update the underlying database.
    sql = """CREATE VIEW officestaffview AS
          SELECT
            p.patient_id,
            MAX(pgp_sym_decrypt(p.first_name, %s)) AS first_name,
            MAX(pgp_sym_decrypt(p.middle_name, %s)) AS middle_name,
            MAX(pgp_sym_decrypt(p.last_name, %s)) AS last_name,
            MAX(pgp_sym_decrypt(p.mailing_address, %s)) AS mailing_address,
            MAX(pgp_sym_decrypt(i.carrier_name, %s)) AS insurance_carrier,
            MAX(pgp_sym_decrypt(i.account_number, %s)) AS insurance_account,
            MAX(pgp_sym_decrypt(i.group_number, %s)) AS insurance_group,
            MAX(CASE WHEN pn.phone_type = 'Home' THEN pgp_sym_decrypt(pn.phone_number, %s) END) AS home_phone,
            MAX(CASE WHEN pn.phone_type = 'Work' THEN pgp_sym_decrypt(pn.phone_number, %s) END) AS work_phone,
            MAX(CASE WHEN pn.phone_type = 'Mobile' THEN pgp_sym_decrypt(pn.phone_number, %s) END) AS mobile_phone,
            MAX(CASE WHEN ec.contact_order = 1 THEN pgp_sym_decrypt(ec.contact_name, %s) END) AS ec1_name,
            MAX(CASE WHEN ec.contact_order = 1 THEN pgp_sym_decrypt(ec.contact_phone, %s) END) AS ec1_phone,
            MAX(CASE WHEN ec.contact_order = 2 THEN pgp_sym_decrypt(ec.contact_name, %s) END) AS ec2_name,
            MAX(CASE WHEN ec.contact_order = 2 THEN pgp_sym_decrypt(ec.contact_phone, %s) END) AS ec2_phone
          FROM Patient p
          LEFT JOIN Insurance i ON p.patient_id = i.patient_id
          LEFT JOIN PhoneNumber pn ON p.patient_id = pn.patient_id
          LEFT JOIN EmergencyContact ec ON p.patient_id = ec.patient_id
          GROUP BY p.patient_id;"""
    params = (
      keys[0],
    ) *14
    cursor2.execute(sql, params)
    cursor2.execute("""GRANT SELECT, UPDATE (
                    first_name,
                    middle_name,
                    last_name,
                    mailing_address,
                    insurance_carrier,
                    insurance_account,
                    insurance_group,
                    home_phone,
                    work_phone,
                    mobile_phone,
                    ec1_name, ec1_phone,
                    ec2_name,
                    ec2_phone)
                    ON officestaffview TO officestaff_role;""")
    cursor2.execute("""GRANT SELECT, UPDATE (first_name, last_name, mailing_address) ON Patient TO officestaff_role;""")
    cursor2.execute("""GRANT INSERT, UPDATE ON Insurance TO officestaff_role;""")
    cursor2.execute("""GRANT INSERT, UPDATE, DELETE ON PhoneNumber TO officestaff_role;""")
    cursor2.execute("""GRANT INSERT, UPDATE, DELETE ON EmergencyContact TO officestaff_role;""")
    cursor2.execute("""GRANT USAGE ON SEQUENCE insurance_insurance_id_seq TO officestaff_role;""")
    # Functions For Updating Patient Data
    # Name and Address
    sql = """CREATE OR REPLACE FUNCTION update_office_staff_all()
          RETURNS TRIGGER AS $$
          DECLARE
          encryption_key TEXT := %s;
          BEGIN
            IF NEW.first_name IS DISTINCT FROM OLD.first_name OR
              NEW.middle_name IS DISTINCT FROM OLD.middle_name OR
              NEW.last_name IS DISTINCT FROM OLD.last_name OR
              NEW.mailing_address IS DISTINCT FROM OLD.mailing_address
            THEN
              UPDATE Patient SET
                first_name = pgp_sym_encrypt(NEW.first_name, encryption_key),
                middle_name = pgp_sym_encrypt(NEW.middle_name, encryption_key),
                last_name = pgp_sym_encrypt(NEW.last_name, encryption_key),
                mailing_address = pgp_sym_encrypt(NEW.mailing_address, encryption_key)
              WHERE patient_id = OLD.patient_id;
            END IF;
            IF NEW.insurance_carrier IS DISTINCT FROM OLD.insurance_carrier OR
              NEW.insurance_account IS DISTINCT FROM OLD.insurance_account OR
              NEW.insurance_group IS DISTINCT FROM OLD.insurance_group 
            THEN
              UPDATE Insurance SET
              carrier_name = pgp_sym_encrypt(NEW.insurance_carrier, encryption_key),
              account_number = pgp_sym_encrypt(NEW.insurance_account, encryption_key),
              group_number = pgp_sym_encrypt(NEW.insurance_group, encryption_key)
              WHERE patient_id = OLD.patient_id;
          END IF;
          IF NEW.home_phone IS DISTINCT FROM OLD.home_phone THEN
            PERFORM update_phone(OLD.patient_id, 'Home', NEW.home_phone);
          END IF;
          IF NEW.work_phone IS DISTINCT FROM OLD.work_phone THEN
            PERFORM update_phone(OLD.patient_id, 'Work', NEW.work_phone);
          END IF;
          IF NEW.mobile_phone IS DISTINCT FROM OLD.mobile_phone THEN
            PERFORM update_phone(OLD.patient_id, 'Mobile', NEW.mobile_phone);
          END IF;
          IF NEW.ec1_name IS DISTINCT FROM OLD.ec1_name OR
            NEW.ec1_phone IS DISTINCT FROM OLD.ec1_phone 
          THEN
            PERFORM update_emergency_contact(OLD.patient_id, 1, NEW.ec1_name, NEW.ec1_phone);
          END IF;
          IF NEW.ec2_name IS DISTINCT FROM OLD.ec2_name OR
            NEW.ec2_phone IS DISTINCT FROM OLD.ec2_phone 
          THEN
            PERFORM update_emergency_contact(OLD.patient_id, 2, NEW.ec2_name, NEW.ec2_phone);
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;"""
    params = (keys[0],)
    cursor2.execute(sql, params)
    cursor2.execute("""ALTER FUNCTION update_office_staff_all() OWNER TO admin_role;""")
    sql = """CREATE OR REPLACE FUNCTION update_phone(
          patient_id INT,
          phone_type TEXT, 
          new_number TEXT
        ) RETURNS VOID AS $$
        DECLARE
          encryption_key TEXT := %s;
      BEGIN
        IF new_number IS NULL THEN
          DELETE FROM PhoneNumber 
          WHERE PhoneNumber.patient_id = update_phone.patient_id AND PhoneNumber.phone_type = update_phone.phone_type;
        ELSE
          UPDATE PhoneNumber
          SET phone_number = pgp_sym_encrypt(new_number, encryption_key)
          WHERE PhoneNumber.patient_id = update_phone.patient_id AND PhoneNumber.phone_type = update_phone.phone_type;
        END IF;
      END;
      $$ LANGUAGE plpgsql;"""
    params = (keys[0],)
    cursor2.execute(sql, params)
    cursor2.execute("""ALTER FUNCTION update_phone(patient_id INT, phone_type TEXT, new_number TEXT) OWNER TO admin_role;""")
    sql = """CREATE OR REPLACE FUNCTION update_emergency_contact(
        patient_id INT,
        contact_order INT, 
        new_name TEXT, 
        new_phone TEXT
      ) RETURNS VOID AS $$
      DECLARE
        encryption_key TEXT := %s;
      BEGIN
        IF new_name IS NULL AND new_phone IS NULL THEN
          DELETE FROM EmergencyContact 
          WHERE EmergencyContact.patient_id = update_emergency_contact.patient_id AND EmergencyContact.contact_order = update_emergency_contact.contact_order;
        ELSE
          UPDATE EmergencyContact SET
            contact_name = pgp_sym_encrypt(new_name, encryption_key),
            contact_phone = pgp_sym_encrypt(new_phone, encryption_key)
          WHERE EmergencyContact.patient_id = update_emergency_contact.patient_id AND EmergencyContact.contact_order = update_emergency_contact.contact_order;
        END IF;
      END;
      $$ LANGUAGE plpgsql;"""
    params = (keys[0],)
    cursor2.execute(sql, params)
    cursor2.execute("""ALTER FUNCTION update_emergency_contact(patient_id INT, contact_order INT, new_name TEXT, new_phone TEXT) OWNER TO admin_role;""")
    sql = """CREATE TRIGGER office_staff_view_update
      INSTEAD OF UPDATE ON officestaffview
      FOR EACH ROW
      EXECUTE FUNCTION update_office_staff_all();"""
    cursor2.execute(sql, params)
  
    # Medical Personnel View
    sql = """CREATE VIEW MedicalPersonnelView AS
          SELECT
            p.patient_id,
            pgp_sym_decrypt(p.first_name, %s) AS first_name,
            pgp_sym_decrypt(p.last_name, %s) AS last_name,
            a.admission_id,
            pgp_sym_decrypt(a.admittance_datetime, %s) AS admittance_datetime,
            pgp_sym_decrypt(pn.note_text, %s) AS doctor_note,
            pgp_sym_decrypt(pn.note_datetime, %s) AS doctor_note_time,
            pgp_sym_decrypt(pr.medication_name, %s) AS medication_name,
            pgp_sym_decrypt(pr.dosage, %s) AS dosage,
            pgp_sym_decrypt(sp.procedure_name, %s) AS procedure_name,
            pgp_sym_decrypt(sp.scheduled_datetime, %s) AS scheduled_datetime,
            NULL AS nurse_note_text
          FROM Patient p JOIN Admission a ON p.patient_id = a.patient_id
          LEFT JOIN PatientNote pn ON a.admission_id = pn.admission_id AND pn.note_type = 'Doctor'
          LEFT JOIN Prescription pr ON a.admission_id = pr.admission_id
          LEFT JOIN ScheduledProcedure sp ON a.admission_id = sp.admission_id;"""
    
    # Create Trigger to remove unneeded visitor data after admission closes
    sql = """CREATE OR REPLACE FUNCTION delete_approved_visitors_on_discharge()
          RETURNS TRIGGER AS $$
          DECLARE
          old_discharge_text TEXT;
          new_discharge_text TEXT;
          BEGIN
            old_discharge_text := pgp_sym_decrypt(OLD.discharge_datetime, %s);
            new_discharge_text := pgp_sym_decrypt(NEW.discharge_datetime, %s);
            IF old_discharge_text IS NULL AND new_discharge_text != 'None' THEN
            DELETE FROM ApprovedVisitors
            WHERE admission_id = NEW.admission_id;
          END IF;
        RETURN NEW;
      END; $$
      LANGUAGE plpgsql SECURITY DEFINER;"""
    params = (
      keys[0],
      keys[0]
    )
    cursor2.execute(sql, params)
    cursor2.execute("""ALTER FUNCTION delete_approved_visitors_on_discharge() OWNER TO admin_role;""")
    cursor2.execute("""CREATE TRIGGER after_discharge_cleanup
                    AFTER UPDATE OF discharge_datetime ON Admission
                    FOR EACH ROW
                    EXECUTE FUNCTION delete_approved_visitors_on_discharge();""")
    
    # Close second connections
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