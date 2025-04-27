import psycopg2
from InsertData import log_action
from contextlib import contextmanager
from EncryptionKey import getKeys

global_connection = None

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
    createConnection()
    with get_cursor() as cursor2:
      cursor2.execute("""SELECT set_config(
            'app.current_user', 
            'Initial User',
            false
          );""")
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
                      username_hash TEXT NOT NULL UNIQUE,
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
      # 15. Active User
      cursor2.execute("""CREATE TABLE activeuser (
                      user_id INT,
                      username_hash TEXT);""")
      # 16. Audit Log
      cursor2.execute("""CREATE TABLE auditlog (
                        log_id SERIAL PRIMARY KEY,
                        username VARCHAR(50) NOT NULL,
                        action_text TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL
                    );""")
      # Adding Indexes for Faster Searching and Partial Searching.
      cursor2.execute("CREATE INDEX idx_staff_username_hash ON Staff USING HASH (username_hash);")
      cursor2.execute("CREATE INDEX idx_staff_first_name_prefix_trgms ON Staff USING gin (first_name_prefix_trgms);")
      cursor2.execute("CREATE INDEX idx_staff_last_name_prefix_trgms ON Staff USING gin (last_name_prefix_trgms);")
      cursor2.execute("CREATE INDEX idx_first_name_prefix_trgms ON Patient USING gin (first_name_prefix_trgms);")
      cursor2.execute("CREATE INDEX idx_middle_name_prefix_trgms ON Patient USING gin (middle_name_prefix_trgms);")
      cursor2.execute("CREATE INDEX idx_last_name_prefix_trgms ON Patient USING gin (last_name_prefix_trgms);")
      cursor2.execute("CREATE INDEX idx_audit_log_timestamp ON auditlog(timestamp);")
      cursor2.execute("CREATE INDEX idx_audit_log_username ON auditlog(username);")
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
      if not ('medicalpersonnel_role' in roles):
        cursor2.execute("CREATE ROLE medicalpersonnel_role;")
        print("Created Medical Personnel Role!")
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

      # Permissions for Inserting Data
      cursor2.execute("GRANT INSERT ON patient TO medicalpersonnel_role, physician_role, officestaff_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE patient_patient_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE approvedvisitors_visitors_id_seq TO medicalpersonnel_role, physician_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE staff_user_id_seq TO administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE location_location_id_seq TO administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE admission_admission_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE billingdetail_billing_detail_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE billing_billing_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE auditlog_log_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role, volunteer_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE insurance_insurance_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE prescription_prescription_id_seq TO medicalpersonnel_role, physician_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE scheduledprocedure_procedure_id_seq TO medicalpersonnel_role, physician_role, administrator_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE patientnote_note_id_seq TO medicalpersonnel_role, physician_role, administrator_role;")
      cursor2.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON emergencycontact TO officestaff_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE emergencycontact_contact_id_seq TO medicalpersonnel_role, physician_role, officestaff_role, administrator_role;")
      # Create Views for Accessing Data
      # patientsearchview is the table used for the search screen, accessible to all user roles
      sql = """CREATE VIEW patientsearchview AS
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
      cursor2.execute("GRANT SELECT ON patientsearchview TO volunteer_role, officestaff_role, medicalpersonnel_role, physician_role;")
      cursor2.execute("GRANT SELECT ON admission TO volunteer_role;")
       # staffsearchview is the table used for the staff search screen, accessible to all admins, office staff, physicians, and medical personnel
      sql = """CREATE VIEW staffsearchview AS
                      SELECT
                      user_id,
                      pgp_sym_decrypt(username, %s) AS username,
                      pgp_sym_decrypt(first_name, %s) AS first_name,
                      pgp_sym_decrypt(last_name, %s) AS last_name,
                      first_name_prefix_trgms,
                      last_name_prefix_trgms,
                      type_name
                    FROM staff NATURAL JOIN usertype;"""
      params = (
        keys[0],
        keys[0],
        keys[0]
      )
      cursor2.execute(sql, params)
      cursor2.execute("GRANT SELECT ON staffsearchview TO officestaff_role, medicalpersonnel_role, physician_role;")
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
      cursor2.execute("GRANT SELECT (admission_id) ON approvedvisitors TO volunteer_role;")
      # BillingInformationView for accessing billing information
      cursor2.execute("""CREATE VIEW BillingInformationView AS
                      SELECT 
                        b.billing_id,
                        b.admission_id,
                        b.total_amount_owed::DECIMAL(10,2) AS amount_owed,
                        b.total_amount_paid::DECIMAL(10,2) AS amount_paid,
                        b.insurance_paid::DECIMAL(10,2) AS insurance_paid,
                        (b.total_amount_owed - b.total_amount_paid - b.insurance_paid)::DECIMAL(10,2) AS balance_due,
                        (
                          SELECT jsonb_agg(
                            jsonb_build_object(
                              'item_id', bd.billing_detail_id,
                              'description', bd.item_description,
                              'charge', bd.charge_amount::DECIMAL(10,2)
                            ) ORDER BY bd.billing_detail_id ASC
                          )
                          FROM BillingDetail bd
                          WHERE bd.billing_id = b.billing_id
                        ) AS billing_items
                      FROM 
                        Billing b
                      JOIN Admission a ON b.admission_id = a.admission_id;""")
      cursor2.execute("GRANT SELECT ON billinginformationview TO officestaff_role, physician_role, medicalpersonnel_role;")
      cursor2.execute("GRANT SELECT ON billing TO officestaff_role, physician_role, medicalpersonnel_role;")
      cursor2.execute("GRANT INSERT, UPDATE ON billing TO officestaff_role, physician_role, medicalpersonnel_role;")
      cursor2.execute("GRANT SELECT ON billingdetail TO officestaff_role, physician_role, medicalpersonnel_role;")
      #Activeadmissionview shows all active admissions
      cursor2.execute("""CREATE VIEW activeadmissionview AS
                      SELECT admission_id, location_id FROM admission WHERE discharge_datetime IS NULL;""")
      cursor2.execute("GRANT SELECT ON activeadmissionview TO officestaff_role, medicalpersonnel_role, physician_role;")
      cursor2.execute("GRANT SELECT, UPDATE ON admission TO officestaff_role, medicalpersonnel_role, physician_role;")
      #Availablelocationview shows all locations without an active admission
      cursor2.execute("""CREATE VIEW availablelocationview AS
                      SELECT l.location_id, l.facility, l.floor, l.room_number, l.bed_number
                      FROM location l
                      WHERE NOT EXISTS(
                      SELECT 1 FROM activeadmissionview a WHERE a.location_ID = l.location_id)
                      ORDER BY l.location_id ASC;""")
      cursor2.execute("GRANT SELECT ON availablelocationview TO officestaff_role, medicalpersonnel_role, physician_role;")
      cursor2.execute("GRANT SELECT ON location TO officestaff_role, medicalpersonnel_role, physician_role;")
      # ActiveLocationView to find locations and patients
      cursor2.execute("""
      CREATE VIEW ActiveLocationView AS
      SELECT 
          p.patient_id,
          l.location_id,
          l.facility,
          l.floor,
          l.room_number,
          l.bed_number,
          a.admission_id,
          a.doctor_id,
          pgp_sym_decrypt(a.admittance_datetime, %s) AS admission_date,
          s.user_id,
          pgp_sym_decrypt(s.first_name, %s) AS doctor_first_name,
          pgp_sym_decrypt(s.last_name, %s) AS doctor_last_name
      FROM 
          Patient p
      JOIN 
          Admission a ON p.patient_id = a.patient_id
      JOIN 
          Location l ON a.location_id = l.location_id
      JOIN
          Staff s ON a.doctor_id = s.user_id
      WHERE 
          a.discharge_datetime IS NULL OR pgp_sym_decrypt(a.discharge_datetime, %s) = 'None';
      """, (keys[0], keys[0], keys[0], keys[0]))

      cursor2.execute("GRANT SELECT ON ActiveLocationView TO volunteer_role, officestaff_role, medicalpersonnel_role, physician_role;")
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
              MAX(CASE WHEN ec.contact_order = 2 THEN pgp_sym_decrypt(ec.contact_phone, %s) END) AS ec2_phone,
              (
                SELECT jsonb_agg(
                  jsonb_build_object(
                    'admission_id', a.admission_id
                  ) ORDER BY a.admittance_datetime DESC
                )
                FROM Admission a
                WHERE a.patient_id = p.patient_id
              ) AS admissions
            FROM Patient p
            LEFT JOIN Insurance i ON p.patient_id = i.patient_id
            LEFT JOIN PhoneNumber pn ON p.patient_id = pn.patient_id
            LEFT JOIN EmergencyContact ec ON p.patient_id = ec.patient_id
            GROUP BY p.patient_id;"""
      params = (
        keys[0],
      ) *14
      cursor2.execute(sql, params)
      cursor2.execute("GRANT INSERT ON auditlog TO volunteer_role, medicalpersonnel_role, administrator_role, officestaff_role, physician_role;")
      cursor2.execute("""GRANT SELECT, UPDATE ON officestaffview TO officestaff_role, physician_role, medicalpersonnel_role;""")
      cursor2.execute("""GRANT SELECT ON officestaffview TO physician_role, medicalpersonnel_role;""")
      cursor2.execute("""GRANT SELECT, UPDATE (first_name, last_name, mailing_address) ON Patient TO officestaff_role, physician_role, medicalpersonnel_role;""")
      cursor2.execute("""GRANT INSERT, UPDATE ON Insurance TO officestaff_role, physician_role, medicalpersonnel_role;""")
      cursor2.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON insurance TO officestaff_role;")
      # Permissions for emergencycontact table
      cursor2.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON emergencycontact TO officestaff_role;")
      cursor2.execute("GRANT USAGE, SELECT ON SEQUENCE emergencycontact_contact_id_seq TO officestaff_role;")
      cursor2.execute("""GRANT INSERT, UPDATE, DELETE ON PhoneNumber TO officestaff_role, physician_role, medicalpersonnel_role;""")
      cursor2.execute("""GRANT INSERT, UPDATE, DELETE ON EmergencyContact TO officestaff_role, physician_role, medicalpersonnel_role;""")
      # Functions For Updating Patient Data
      # Name and Address
      sql = """CREATE OR REPLACE FUNCTION update_office_staff_all()
                RETURNS TRIGGER AS $$
                DECLARE
                encryption_key TEXT := %s;
                old_values TEXT;
                new_values TEXT;
                action_details TEXT;
                BEGIN
                  old_values := '';
                  new_values := '';
                  action_details := '';
                  
                  IF NEW.first_name IS DISTINCT FROM OLD.first_name OR
                    NEW.middle_name IS DISTINCT FROM OLD.middle_name OR
                    NEW.last_name IS DISTINCT FROM OLD.last_name OR
                    NEW.mailing_address IS DISTINCT FROM OLD.mailing_address
                  THEN
                    old_values := 'Old values: ' || COALESCE(OLD.first_name, 'NULL') || ', ' || 
                                  COALESCE(OLD.middle_name, 'NULL') || ', ' ||
                                  COALESCE(OLD.last_name, 'NULL') || ', ' ||
                                  COALESCE(OLD.mailing_address, 'NULL');
                    new_values := 'New values: ' || COALESCE(NEW.first_name, 'NULL') || ', ' || 
                                  COALESCE(NEW.middle_name, 'NULL') || ', ' ||
                                  COALESCE(NEW.last_name, 'NULL') || ', ' ||
                                  COALESCE(NEW.mailing_address, 'NULL');
                    action_details := 'Updated patient basic info for patient_id ' || OLD.patient_id;

                    
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
                    old_values := 'Old insurance: ' || COALESCE(OLD.insurance_carrier, 'NULL') || ', ' || 
                                COALESCE(OLD.insurance_account, 'NULL') || ', ' ||
                                COALESCE(OLD.insurance_group, 'NULL');
                    new_values := 'New insurance: ' || COALESCE(NEW.insurance_carrier, 'NULL') || ', ' || 
                                COALESCE(NEW.insurance_account, 'NULL') || ', ' ||
                                COALESCE(NEW.insurance_group, 'NULL');
                    action_details := 'Updated insurance info for patient_id ' || OLD.patient_id;
                    
                    UPDATE Insurance SET
                    carrier_name = pgp_sym_encrypt(NEW.insurance_carrier, encryption_key),
                    account_number = pgp_sym_encrypt(NEW.insurance_account, encryption_key),
                    group_number = pgp_sym_encrypt(NEW.insurance_group, encryption_key)
                    WHERE patient_id = OLD.patient_id;
                  END IF;
                  
                  IF NEW.home_phone IS DISTINCT FROM OLD.home_phone THEN
                    old_values := 'Old home phone: ' || COALESCE(OLD.home_phone, 'NULL');
                    new_values := 'New home phone: ' || COALESCE(NEW.home_phone, 'NULL');
                    action_details := 'Updated home phone for patient_id ' || OLD.patient_id;

                    PERFORM update_phone(OLD.patient_id, 'Home', NEW.home_phone);
                  END IF;
                  
                  IF NEW.work_phone IS DISTINCT FROM OLD.work_phone THEN
                    old_values := 'Old work phone: ' || COALESCE(OLD.work_phone, 'NULL');
                    new_values := 'New work phone: ' || COALESCE(NEW.work_phone, 'NULL');
                    action_details := 'Updated work phone for patient_id ' || OLD.patient_id;
                    
                    PERFORM update_phone(OLD.patient_id, 'Work', NEW.work_phone);
                  END IF;
                  
                  IF NEW.mobile_phone IS DISTINCT FROM OLD.mobile_phone THEN
                    old_values := 'Old mobile phone: ' || COALESCE(OLD.mobile_phone, 'NULL');
                    new_values := 'New mobile phone: ' || COALESCE(NEW.mobile_phone, 'NULL');
                    action_details := 'Updated mobile phone for patient_id ' || OLD.patient_id;
                    
                    PERFORM update_phone(OLD.patient_id, 'Mobile', NEW.mobile_phone);
                  END IF;
                  
                  IF NEW.ec1_name IS DISTINCT FROM OLD.ec1_name OR
                    NEW.ec1_phone IS DISTINCT FROM OLD.ec1_phone 
                  THEN
                    old_values := 'Old emergency contact 1: ' || COALESCE(OLD.ec1_name, 'NULL') || ', ' || 
                                COALESCE(OLD.ec1_phone, 'NULL');
                    new_values := 'New emergency contact 1: ' || COALESCE(NEW.ec1_name, 'NULL') || ', ' || 
                                COALESCE(NEW.ec1_phone, 'NULL');
                    action_details := 'Updated emergency contact 1 for patient_id ' || OLD.patient_id;
                    
                    PERFORM update_emergency_contact(OLD.patient_id, 1, NEW.ec1_name, NEW.ec1_phone);
                  END IF;
                  
                  IF NEW.ec2_name IS DISTINCT FROM OLD.ec2_name OR
                    NEW.ec2_phone IS DISTINCT FROM OLD.ec2_phone 
                  THEN
                    old_values := 'Old emergency contact 2: ' || COALESCE(OLD.ec2_name, 'NULL') || ', ' || 
                                COALESCE(OLD.ec2_phone, 'NULL');
                    new_values := 'New emergency contact 2: ' || COALESCE(NEW.ec2_name, 'NULL') || ', ' || 
                                COALESCE(NEW.ec2_phone, 'NULL');
                    action_details := 'Updated emergency contact 2 for patient_id ' || OLD.patient_id;
                    
                    PERFORM update_emergency_contact(OLD.patient_id, 2, NEW.ec2_name, NEW.ec2_phone);
                  END IF;

                  RETURN NEW;
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("""ALTER FUNCTION update_office_staff_all() OWNER TO administrator_role;""")
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
      cursor2.execute("""ALTER FUNCTION update_phone(patient_id INT, phone_type TEXT, new_number TEXT) OWNER TO administrator_role;""")
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
      cursor2.execute("""ALTER FUNCTION update_emergency_contact(patient_id INT, contact_order INT, new_name TEXT, new_phone TEXT) OWNER TO administrator_role;""")
      sql = """CREATE TRIGGER office_staff_view_update
        INSTEAD OF UPDATE ON officestaffview
        FOR EACH ROW
        EXECUTE FUNCTION update_office_staff_all();"""
      cursor2.execute(sql, params)
      # Physician and Medical Personnel
      # Patient Admission View for Physicians and Medical Personnel
      sql = """CREATE VIEW PatientAdmissionOverview AS
              SELECT 
                p.patient_id,
                pgp_sym_decrypt(p.first_name, %s) AS first_name,
                pgp_sym_decrypt(p.middle_name, %s) AS middle_name,
                pgp_sym_decrypt(p.last_name, %s) AS last_name,
                pgp_sym_decrypt(p.mailing_address, %s) AS mailing_address,
                pgp_sym_decrypt(i.carrier_name, %s) AS insurance_carrier,
                pgp_sym_decrypt(i.account_number, %s) AS insurance_account,
                pgp_sym_decrypt(i.group_number, %s) AS insurance_group,
                (SELECT pgp_sym_decrypt(pn.phone_number, %s) FROM PhoneNumber pn 
                WHERE pn.patient_id = p.patient_id AND pn.phone_type = 'Home' LIMIT 1) AS home_phone,
                (SELECT pgp_sym_decrypt(pn.phone_number, %s) FROM PhoneNumber pn 
                WHERE pn.patient_id = p.patient_id AND pn.phone_type = 'Work' LIMIT 1) AS work_phone,
                (SELECT pgp_sym_decrypt(pn.phone_number, %s) FROM PhoneNumber pn 
                WHERE pn.patient_id = p.patient_id AND pn.phone_type = 'Mobile' LIMIT 1) AS mobile_phone,
                (SELECT pgp_sym_decrypt(ec.contact_name, %s) FROM EmergencyContact ec 
                WHERE ec.patient_id = p.patient_id AND ec.contact_order = 1 LIMIT 1) AS ec1_name,
                (SELECT pgp_sym_decrypt(ec.contact_phone, %s) FROM EmergencyContact ec 
                WHERE ec.patient_id = p.patient_id AND ec.contact_order = 1 LIMIT 1) AS ec1_phone,
                (SELECT pgp_sym_decrypt(ec.contact_name, %s) FROM EmergencyContact ec 
                WHERE ec.patient_id = p.patient_id AND ec.contact_order = 2 LIMIT 1) AS ec2_name,
                (SELECT pgp_sym_decrypt(ec.contact_phone, %s) FROM EmergencyContact ec 
                WHERE ec.patient_id = p.patient_id AND ec.contact_order = 2 LIMIT 1) AS ec2_phone,
                (
                  SELECT jsonb_agg(
                    jsonb_build_object(
                      'admission_id', a.admission_id,
                      'admittance_date', pgp_sym_decrypt(a.admittance_datetime, %s),
                      'admission_reason', pgp_sym_decrypt(a.reason_for_admission, %s),
                      'admittance_discharge', pgp_sym_decrypt(a.discharge_datetime, %s),
                      'approved_visitors', (
                        SELECT ARRAY (
                          SELECT pgp_sym_decrypt(visitor, %s)
                          FROM unnest(v.names) AS visitor
                        )
                        FROM ApprovedVisitors v
                        WHERE v.admission_id = a.admission_id
                      ),
                      'details', jsonb_build_object(
                        'notes', (
                          SELECT jsonb_agg(
                            jsonb_build_object(
                              'text', pgp_sym_decrypt(pn.note_text, %s),
                              'type', pn.note_type,
                              'author', pgp_sym_decrypt(s.first_name, %s) || ' ' || pgp_sym_decrypt(s.last_name, %s),
                              'datetime', pgp_sym_decrypt(pn.note_datetime, %s)
                            )
                          )
                          FROM PatientNote pn
                          JOIN Staff s ON pn.author_id = s.user_id
                          WHERE pn.admission_id = a.admission_id
                        ),
                        'prescriptions', (
                          SELECT jsonb_agg(
                            jsonb_build_object(
                              'medication', pgp_sym_decrypt(pr.medication_name, %s),
                              'amount', pgp_sym_decrypt(pr.amount, %s),
                              'schedule', pgp_sym_decrypt(pr.schedule, %s)
                            )
                          )
                          FROM Prescription pr
                          WHERE pr.admission_id = a.admission_id
                        ),
                        'procedures', (
                          SELECT jsonb_agg(
                            jsonb_build_object(
                              'name', pgp_sym_decrypt(sp.procedure_name, %s),
                              'scheduled', pgp_sym_decrypt(sp.scheduled_datetime, %s)
                            )
                          )
                          FROM ScheduledProcedure sp
                          WHERE sp.admission_id = a.admission_id
                        )
                      )
                    ) ORDER BY a.admittance_datetime DESC
                  )
                  FROM Admission a
                  WHERE a.patient_id = p.patient_id
                ) AS admissions
              FROM Patient p
              LEFT JOIN Insurance i ON p.patient_id = i.patient_id
              GROUP BY p.patient_id, p.first_name, p.middle_name, p.last_name, p.mailing_address, 
                      i.carrier_name, i.account_number, i.group_number;"""
      params = (keys[0],)*27
      cursor2.execute(sql, params)
      cursor2.execute("GRANT SELECT ON patientadmissionoverview TO medicalpersonnel_role;")
      cursor2.execute("GRANT SELECT, DELETE ON approvedvisitors TO medicalpersonnel_role, physician_role, officestaff_role;")
      cursor2.execute("GRANT SELECT ON patientadmissionoverview TO physician_role;")
      # staffwriteview allows insertion of staff members information
      sql = """CREATE VIEW staffwriteview AS
                SELECT
                  NULL::TEXT AS first_name,
                  NULL::TEXT AS last_name,
                  NULL::TEXT[] AS first_name_prefix_trgms,
                  NULL::TEXT[] AS last_name_prefix_trgms,
                  NULL::TEXT AS username,
                  NULL::TEXT AS password,
                  NULL::INT AS type_id;"""
      cursor2.execute(sql)
      # triggers and functions for adding staff member to database
      sql = """CREATE OR REPLACE FUNCTION staff_write_trigger()
              RETURNS TRIGGER AS $$
              DECLARE
                encryption_key TEXT := %s;
                fixed_salt TEXT := %s;
              BEGIN
              INSERT INTO staff (
                  first_name,
                  last_name,
                  first_name_prefix_trgms,
                  last_name_prefix_trgms,
                  username_hash,
                  username,
                  password_hash,
                  type_id
                ) VALUES (
                  pgp_sym_encrypt(NEW.first_name, encryption_key),
                  pgp_sym_encrypt(NEW.last_name, encryption_key),
                  NEW.first_name_prefix_trgms,
                  NEW.last_name_prefix_trgms,
                  encode(digest(NEW.username || fixed_salt, 'sha256'), 'hex'),
                  pgp_sym_encrypt(NEW.username, encryption_key),
                  crypt(NEW.password, gen_salt('bf')),
                  NEW.type_id
                );
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0], keys[1])
      cursor2.execute(sql, params)
      cursor2.execute("ALTER FUNCTION staff_write_trigger() OWNER TO administrator_role;")
      cursor2.execute("""CREATE TRIGGER staff_write_trigger
                      INSTEAD OF UPDATE ON staffwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION staff_write_trigger();""")
      # patientwriteview allows insertion of patient information
      sql = """CREATE VIEW patientwriteview AS
                SELECT
                  NULL::TEXT AS first_name,
                  NULL::TEXT AS middle_name,
                  NULL::TEXT AS last_name,
                  NULL::TEXT[] AS first_name_prefix_trgms,
                  NULL::TEXT[] AS middle_name_prefix_trgms,
                  NULL::TEXT[] AS last_name_prefix_trgms,
                  NULL::TEXT AS mailing_address,
                  NULL::INT AS family_doctor_id;"""
      cursor2.execute(sql)
      cursor2.execute("GRANT UPDATE ON patientwriteview TO officestaff_role, medicalpersonnel_role, physician_role;")
      # triggers and functions for adding patient to database
      sql = """CREATE OR REPLACE FUNCTION patient_write_trigger()
              RETURNS TRIGGER AS $$
              DECLARE
                encryption_key TEXT := %s;
                new_patient_id INTEGER;
              BEGIN
              INSERT INTO Patient (
                  first_name,
                  middle_name,
                  last_name,
                  first_name_prefix_trgms,
                  middle_name_prefix_trgms,
                  last_name_prefix_trgms,
                  mailing_address,
                  family_doctor_id
                ) VALUES (
                  pgp_sym_encrypt(NEW.first_name, encryption_key),
                  pgp_sym_encrypt(NEW.middle_name, encryption_key),
                  pgp_sym_encrypt(NEW.last_name, encryption_key),
                  NEW.first_name_prefix_trgms,
                  NEW.middle_name_prefix_trgms,
                  NEW.last_name_prefix_trgms,
                  pgp_sym_encrypt(NEW.mailing_address, encryption_key),
                  NEW.family_doctor_id
                ) RETURNING patient_id INTO new_patient_id;
                INSERT INTO phonenumber (
                patient_id,
                phone_type,
                phone_number
                ) VALUES
                  (new_patient_id, 'Home', pgp_sym_encrypt(NULL, encryption_key)),
                  (new_patient_id, 'Mobile', pgp_sym_encrypt(NULL, encryption_key)),
                  (new_patient_id, 'Work', pgp_sym_encrypt(NULL, encryption_key));
                INSERT INTO emergencycontact (
                patient_id,
                contact_name,
                contact_phone,
                contact_order
                ) VALUES
                  (new_patient_id, pgp_sym_encrypt(NULL, encryption_key),  pgp_sym_encrypt(NULL, encryption_key), 1),
                  (new_patient_id, pgp_sym_encrypt(NULL, encryption_key),  pgp_sym_encrypt(NULL, encryption_key), 2);
                INSERT INTO Insurance (
                patient_id,
                carrier_name,
                account_number,
                group_number
                ) VALUES
                  (new_patient_id, pgp_sym_encrypt(NULL, encryption_key),  pgp_sym_encrypt(NULL, encryption_key), pgp_sym_encrypt(NULL, encryption_key));
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("""CREATE TRIGGER patient_write_trigger
                      INSTEAD OF UPDATE ON patientwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION patient_write_trigger();""")
      # Locationwriteview for adding a location
      cursor2.execute("""CREATE VIEW locationwriteview AS
                SELECT
                  NULL::TEXT AS facility,
                  NULL::INT AS floor,
                  NULL::INT AS room,
                  NULL::INT AS bed;""")
      # Trigger For inserting Location Data to database
      sql = """CREATE OR REPLACE FUNCTION location_write_trigger()
            RETURNS TRIGGER AS $$
            DECLARE
              encryption_key TEXT := %s;
            BEGIN
              INSERT INTO location (
                  facility, 
                  floor,
                  room_number,
                  bed_number
              ) VALUES (
                NEW.facility,
                NEW.floor,
                NEW.room,
                NEW.bed
              );
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("""CREATE TRIGGER location_write_trigger
                      INSTEAD OF UPDATE ON locationwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION location_write_trigger();""")
      # Admission Write view for inserting admissions
      sql = """CREATE VIEW admissionwriteview AS
                SELECT
                  patient_id,
                  NULL::INT AS location_id,
                  NULL::INT AS doctor_id,
                  NULL::TEXT AS admittance_datetime,
                  NULL::TEXT AS reason_for_admission
                FROM patient;"""
      cursor2.execute(sql)
      # Triggers and Functions for Updating admission in the database
      sql = """CREATE OR REPLACE FUNCTION admission_write_trigger()
              RETURNS TRIGGER AS $$
              DECLARE
                encryption_key TEXT := %s;
              BEGIN
                INSERT INTO admission (
                    patient_id, 
                    location_id,
                    doctor_id,
                    admittance_datetime,
                    reason_for_admission,
                    discharge_datetime
                ) VALUES (
                  NEW.patient_id,
                  NEW.location_id,
                  NEW.doctor_id,
                  pgp_sym_encrypt(NEW.admittance_datetime, encryption_key),
                  pgp_sym_encrypt(NEW.reason_for_admission, encryption_key),
                  pgp_sym_encrypt(NULL, encryption_key)
                );
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("ALTER FUNCTION admission_write_trigger() OWNER TO administrator_role;")

      cursor2.execute("""CREATE TRIGGER admission_write_trigger
                      INSTEAD OF UPDATE ON admissionwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION admission_write_trigger();""")
      cursor2.execute("GRANT SELECT, UPDATE ON admissionwriteview TO officestaff_role, medicalpersonnel_role, physician_role;")
      cursor2.execute("GRANT INSERT ON admission TO physician_role, medicalpersonnel_role, officestaff_role;")
      cursor2.execute("GRANT SELECT (admission_id, patient_id) ON admission TO physician_role, medicalpersonnel_role, officestaff_role;")
      #visitorwriteView for addind visitors to an admission
      sql = """CREATE VIEW visitorwriteview AS
            SELECT
              admission_id,
              NULL::BYTEA[] as visitors
            FROM activeadmissionview"""
      cursor2.execute(sql)
      # Triggers for adding visitor to database
      sql = """CREATE OR REPLACE FUNCTION visitor_write_trigger()
              RETURNS TRIGGER AS $$
              BEGIN
                INSERT INTO approvedvisitors (
                    admission_id,
                    names
                ) VALUES (
                  NEW.admission_id,
                  NEW.visitors
                );
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      cursor2.execute(sql)
      cursor2.execute("""CREATE TRIGGER visitor_write_trigger
                      INSTEAD OF UPDATE ON visitorwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION visitor_write_trigger();""")
      cursor2.execute("""GRANT SELECT, UPDATE ON visitorwriteview TO physician_role, medicalpersonnel_role, officestaff_role;""")
      #NurseWriteView for adding nurse notes to an admission
      sql = """CREATE VIEW NurseWriteView AS
            SELECT
              patient_id,
              (jsonb_array_elements(admissions) ->> 'admission_id')::INT AS admission_id,
              'Nurse' AS note_type,
              NULL::TEXT AS note_text
            FROM PatientAdmissionOverview;"""
      cursor2.execute(sql)
      cursor2.execute("""GRANT INSERT ON PatientNote TO medicalpersonnel_role;""")
      cursor2.execute("""GRANT SELECT, UPDATE ON NurseWriteView TO medicalpersonnel_role;""")
      #Functions And Triggers
      # Helper Function To Unnest Admission ID from JSON Data
      sql = """CREATE OR REPLACE FUNCTION get_admission_id(patient_id INT, admission_idx INT)
            RETURNS INT AS $$
            DECLARE
              admission_json jsonb;
            BEGIN
              SELECT admissions INTO admission_json
              FROM PatientAdmissionOverview
              WHERE PatientAdmissionOverview.patient_id = get_admission_id.patient_id;

              RETURN (admission_json -> admission_idx ->> 'admission_id')::INT;
            END;
            $$ LANGUAGE plpgsql STABLE;"""
      cursor2.execute(sql)
      # Function for Inserting nurse notes into database
      sql = """CREATE OR REPLACE FUNCTION nurse_write_trigger()
              RETURNS TRIGGER AS $$
              DECLARE
                encryption_key TEXT := %s;
              BEGIN
                -- Instead of checking against the JSON structure, directly check the admission table
                -- This is much faster as it uses the primary key index
                IF NOT EXISTS (
                  SELECT 1
                  FROM admission a
                  WHERE a.admission_id = NEW.admission_id AND a.patient_id = NEW.patient_id
                ) THEN
                  RAISE EXCEPTION 'Invalid admission_id %% for patient %%', NEW.admission_id, NEW.patient_id;
                END IF;
                
                INSERT INTO PatientNote (
                  admission_id,
                  note_type,
                  note_text,
                  note_datetime,
                  author_id
                ) VALUES (
                  NEW.admission_id,
                  'Nurse',
                  pgp_sym_encrypt(NEW.note_text, encryption_key),
                  pgp_sym_encrypt(NOW()::text, encryption_key),
                  current_setting('app.current_user_id')::INT
                );
                
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("""CREATE TRIGGER nurse_write_trigger
                      INSTEAD OF UPDATE ON NurseWriteView
                      FOR EACH ROW
                      EXECUTE FUNCTION nurse_write_trigger();""")
      # Physician View for Updating Data
      sql = """CREATE VIEW PhysicianWriteView AS
            SELECT
              patient_id,
              (jsonb_array_elements(admissions) ->> 'admission_id')::INT AS admission_id,
              'Doctor' AS note_type,
              NULL::TEXT AS note_text,
              NULL::TEXT AS medication_name,
              NULL::TEXT AS medication_amount,
              NULL::TEXT AS medication_schedule,
              NULL::TEXT AS procedure_name,
              NULL::TEXT AS procedure_schedule
            FROM PatientAdmissionOverview;"""
      cursor2.execute(sql)
      cursor2.execute("""GRANT INSERT ON PatientNote TO physician_role;""")
      cursor2.execute("""GRANT INSERT ON Prescription TO physician_role;""")
      cursor2.execute("""GRANT INSERT ON ScheduledProcedure TO physician_role;""")
      cursor2.execute("""GRANT SELECT, UPDATE ON PhysicianWriteView TO physician_role;""")
      # Function for Inserting physician notes, procedures, and prescriptions into database
      sql = """CREATE OR REPLACE FUNCTION physician_write_trigger()
                RETURNS TRIGGER AS $$
                DECLARE
                  encryption_key TEXT := %s;
                BEGIN
                  -- Use direct table lookup instead of JSON processing
                  IF NOT EXISTS (
                    SELECT 1
                    FROM admission a
                    WHERE a.admission_id = NEW.admission_id AND a.patient_id = NEW.patient_id
                  ) THEN
                    RAISE EXCEPTION 'Invalid admission_id %% for patient %%', NEW.admission_id, NEW.patient_id;
                  END IF;
                  
                  -- Only perform the inserts that are needed based on which fields are populated
                  IF NEW.note_text IS NOT NULL THEN
                    INSERT INTO PatientNote (
                      admission_id,
                      note_type,
                      note_text,
                      note_datetime,
                      author_id
                    ) VALUES (
                      NEW.admission_id,
                      'Doctor',
                      pgp_sym_encrypt(NEW.note_text, encryption_key),
                      pgp_sym_encrypt(NOW()::text, encryption_key),
                      current_setting('app.current_user_id')::INT
                    );
                  END IF;
                  
                  IF NEW.medication_name IS NOT NULL THEN
                    INSERT INTO Prescription (
                      admission_id,
                      medication_name,
                      amount,
                      schedule
                    ) VALUES (
                      NEW.admission_id,
                      pgp_sym_encrypt(NEW.medication_name, encryption_key),
                      pgp_sym_encrypt(NEW.medication_amount, encryption_key),
                      pgp_sym_encrypt(NEW.medication_schedule, encryption_key)
                    );
                  END IF;
                  
                  IF NEW.procedure_name IS NOT NULL THEN
                    INSERT INTO ScheduledProcedure (
                      admission_id,
                      procedure_name,
                      scheduled_datetime
                    ) VALUES (
                      NEW.admission_id,
                      pgp_sym_encrypt(NEW.procedure_name, encryption_key),
                      pgp_sym_encrypt(NEW.procedure_schedule, encryption_key)
                    );
                  END IF;
                  
                  RETURN NEW;
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;"""
      params = (keys[0],)
      cursor2.execute(sql, params)
      cursor2.execute("""CREATE TRIGGER physician_write_trigger
                      INSTEAD OF UPDATE ON PhysicianWriteView
                      FOR EACH ROW
                      EXECUTE FUNCTION Physician_write_trigger();""")
      # billwriteview for inserting data into billing tables
      cursor2.execute("""CREATE VIEW billwriteview AS
                    SELECT 
                        a.admission_id,
                        NULL::TEXT AS billed_item_name,
                        NULL::DECIMAL(10,2) AS billed_item_cost
                    FROM Admission a;
                    """)

      # functions and triggers for adding data to the database
      cursor2.execute("""CREATE OR REPLACE FUNCTION bill_item_trigger()
                  RETURNS TRIGGER AS $$
                  DECLARE
                      new_billing_id INT;
                  BEGIN
                      SELECT b.billing_id INTO new_billing_id 
                      FROM Billing b
                      WHERE b.admission_id = NEW.admission_id;

                      IF NOT FOUND THEN
                          INSERT INTO Billing (admission_id, total_amount_owed, total_amount_paid, insurance_paid)
                          VALUES (NEW.admission_id, 0, 0, 0)
                          RETURNING billing_id INTO new_billing_id;
                      END IF;

                      INSERT INTO BillingDetail (billing_id, item_description, charge_amount)
                      VALUES (new_billing_id, NEW.billed_item_name, NEW.billed_item_cost);

                      RETURN NEW;
                  END;
                  $$ LANGUAGE plpgsql SECURITY DEFINER;
                    """)

      cursor2.execute("""ALTER FUNCTION bill_item_trigger() OWNER TO administrator_role;""")
      # 3. Create trigger for the view
      cursor2.execute("""CREATE TRIGGER bill_item_trigger
                      INSTEAD OF UPDATE ON billwriteview
                      FOR EACH ROW
                      EXECUTE FUNCTION bill_item_trigger();
                      """)

      # 4. Create function to update billing totals
      cursor2.execute("""
                      CREATE OR REPLACE FUNCTION update_billing_totals()
                      RETURNS TRIGGER AS $$
                      BEGIN
                          UPDATE Billing b
                          SET total_amount_owed = (
                              SELECT COALESCE(SUM(charge_amount), 0)
                              FROM BillingDetail bd
                              WHERE bd.billing_id = COALESCE(NEW.billing_id, OLD.billing_id)
                          )
                          WHERE b.billing_id = COALESCE(NEW.billing_id, OLD.billing_id);

                          RETURN NULL;
                      END;
                      $$ LANGUAGE plpgsql;
                      """)
      cursor2.execute("""ALTER FUNCTION update_billing_totals() OWNER TO administrator_role;""")
      # 5. Create triggers for billing detail changes
      cursor2.execute("""CREATE TRIGGER billing_detail_changes
                      AFTER INSERT OR UPDATE OR DELETE ON BillingDetail
                      FOR EACH ROW
                      EXECUTE FUNCTION update_billing_totals();
                      """)

      # 6. Grant permissions
      cursor2.execute("GRANT SELECT, UPDATE ON billwriteview TO physician_role, medicalpersonnel_role, officestaff_role;")
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
      cursor2.execute("""ALTER FUNCTION delete_approved_visitors_on_discharge() OWNER TO administrator_role;""")
      cursor2.execute("""CREATE TRIGGER after_discharge_cleanup
                      AFTER UPDATE OF discharge_datetime ON Admission
                      FOR EACH ROW
                      EXECUTE FUNCTION delete_approved_visitors_on_discharge();""")
      # Give admin all roles
      cursor2.execute("""GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO administrator_role;""")
      # Close second connections
      cursor2.close()
      print("Database Created")
  else:
    print("Database Already Exists")
    createConnection()
  # Close first connections
  cursor.close()
  conn.close()

def createConnection():
  global global_connection
  if global_connection is None or global_connection.closed:
        global_connection = psycopg2.connect(
            database="huntsvillehospital",
            user='postgres',
            password='49910',
            host='localhost',
            port='5432'
        )
        global_connection.autocommit = True

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

if __name__ == "__main__":
  run()