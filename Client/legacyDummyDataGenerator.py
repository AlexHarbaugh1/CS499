import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import random
from decimal import Decimal
import hospitalDB
import EncryptionKey
import InsertData
import UpdateDB
# Initialize Faker and DB connection

def insertStaff(fname , lname, username, password, type, encryptionKey, fixedSalt):

    with hospitalDB.get_cursor() as cursor:
        fnameHashedPrefixes = [InsertData.hashPrefix(prefix, fixedSalt) for prefix in InsertData.generatePrefixes(fname)]
        lnameHashedPrefixes = [InsertData.hashPrefix(prefix, fixedSalt) for prefix in InsertData.generatePrefixes(lname)]
        sql = """INSERT INTO Staff (first_name, last_name, first_name_prefix_trgms, last_name_prefix_trgms, username_hash, username, password_hash, type_id)
                    Values(
                    pgp_sym_encrypt(%s, %s),
                    pgp_sym_encrypt(%s, %s),
                    %s,
                    %s,
                    encode(digest(%s || %s, 'sha256'), 'hex'),
                    pgp_sym_encrypt(%s, %s),
                    crypt(%s, gen_salt('bf')),
                    (SELECT type_id FROM UserType WHERE type_name = %s));"""
        params = (
            fname, encryptionKey,
            lname, encryptionKey,
            fnameHashedPrefixes,
            lnameHashedPrefixes,
            username, fixedSalt,
            username, encryptionKey,
            password,
            type
        )
        cursor.execute(sql, params)
        
def insertPatient(lname, fname, mname, address, hPhone, mPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum, encryptionKey, fixedSalt):

    with hospitalDB.get_cursor() as cursor:
        fnameHashedPrefixes = [InsertData.hashPrefix(prefix, fixedSalt) for prefix in  InsertData.generatePrefixes(fname)]
        if mname != None:
            mnameHashedPrefixes = [ InsertData.hashPrefix(prefix, fixedSalt) for prefix in  InsertData.generatePrefixes(mname)]
        else:
            mnameHashedPrefixes = None
        lnameHashedPrefixes = [ InsertData.hashPrefix(prefix, fixedSalt) for prefix in  InsertData.generatePrefixes(lname)]

        sql = """WITH
        doctor AS (
            SELECT user_id 
            FROM Staff 
            WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex')
        ),
        new_patient AS (
            INSERT INTO Patient (first_name, middle_name, last_name, first_name_prefix_trgms, middle_name_prefix_trgms, last_name_prefix_trgms, mailing_address, family_doctor_id)
            VALUES (
                pgp_sym_encrypt(%s, %s),
                pgp_sym_encrypt(%s, %s),
                pgp_sym_encrypt(%s, %s),
                %s,
                %s,
                %s,
                pgp_sym_encrypt(%s, %s),
                (SELECT user_id FROM doctor)
            )
            RETURNING patient_id
        ),
        phone_numbers AS (
            INSERT INTO PhoneNumber (patient_id, phone_type, phone_number)
            VALUES
                ((SELECT patient_id FROM new_patient), 'Home', pgp_sym_encrypt(%s, %s)),
                ((SELECT patient_id FROM new_patient), 'Mobile', pgp_sym_encrypt(%s, %s)),
                ((SELECT patient_id FROM new_patient), 'Work', pgp_sym_encrypt(%s, %s))
        ),
        emergency_contacts AS (
            INSERT INTO EmergencyContact (patient_id, contact_name, contact_phone, contact_order)
            VALUES
                ((SELECT patient_id FROM new_patient), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), 1),
                ((SELECT patient_id FROM new_patient), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), 2)
        ),
        new_insurance AS (
            INSERT INTO Insurance (patient_id, carrier_name, account_number, group_number)
            VALUES (
                (SELECT patient_id FROM new_patient),
                pgp_sym_encrypt(%s, %s),
                pgp_sym_encrypt(%s, %s),
                pgp_sym_encrypt(%s, %s)
            )
        )
        SELECT 1;"""
 # Pass parameters as a tuple (order matters!)
        params = (
            # Doctor lookup
            doctor, fixedSalt,
            
            # new_patient
            fname, encryptionKey,
            mname, encryptionKey,
            lname, encryptionKey,
            fnameHashedPrefixes,
            mnameHashedPrefixes,
            lnameHashedPrefixes,
            address, encryptionKey,
            
            # phone_numbers
            hPhone, encryptionKey,
            mPhone, encryptionKey,
            wPhone, encryptionKey,
            
            # emergency_contacts
            c1Name, encryptionKey,
            c1Phone, encryptionKey,
            c2Name, encryptionKey,
            c2Phone, encryptionKey,
            
            # new_insurance
            insCarrier, encryptionKey,
            insAcc, encryptionKey,
            insGNum, encryptionKey
        )

        cursor.execute(sql, params)
        
def insertAdmission(patientID, admissionDateTime, admissionReason, releaseDateTime,
                    hospitalFacility, hospitalFloor, hospitalRoom, hospitalBed, doctorID, encryptionKey):

    with hospitalDB.get_cursor() as cursor:
        sql =  """WITH 
            location AS (
                INSERT INTO Location (facility, floor, room_number, bed_number)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT unique_location 
                DO UPDATE SET facility = EXCLUDED.facility
                RETURNING location_id
            ),
            admission AS (
                INSERT INTO Admission (
                    patient_id, 
                    location_id,
                    doctor_id,
                    admittance_datetime,
                    reason_for_admission,
                    discharge_datetime
                )
                VALUES (
                    %s,
                    (SELECT location_id FROM location),
                    %s,
                    pgp_sym_encrypt(%s, %s),
                    pgp_sym_encrypt(%s, %s),
                    pgp_sym_encrypt(%s, %s)
                )
                RETURNING admission_id
                )
                SELECT admission_id FROM admission;"""


            
            
            # Prepare parameters
        params = (

            # Location
            hospitalFacility,
            hospitalFloor,
            hospitalRoom,
            hospitalBed,
                
            # Admission
            patientID,
            doctorID,
            admissionDateTime, encryptionKey,
            admissionReason, encryptionKey,
            str(releaseDateTime) if releaseDateTime else None, encryptionKey,

            
            )
        cursor.execute(sql, params)

        ID = cursor.fetchone()[0]
        

    return ID
def insertVisitors(admissionID, visitorNames, encryptionKey):
    with hospitalDB.get_cursor() as cursor:
        sql = """INSERT INTO approvedvisitors(admission_id)
                SELECT
                %s;"""
        params = (
            admissionID,
            visitorNames,
            encryptionKey
        )
        encryptedNames = []
        for name in visitorNames:
            sql = "SELECT pgp_sym_encrypt(%s, %s) AS encrypted_name;"
            params = (name, encryptionKey)
            cursor.execute(sql, params)
            encryptedNames.append(cursor.fetchone()[0])
        sql = """INSERT INTO approvedvisitors(admission_id, names)
                SELECT
                %s,
                %s;"""
        params = (
            admissionID,
            encryptedNames
        )
        cursor.execute(sql, params)
        
def insertPrescriptions(admissionID, prescriptions, encryptionKey):
    with hospitalDB.get_cursor() as cursor:
        sql = """INSERT INTO Prescription (admission_id, medication_name, amount, schedule)
                SELECT 
                    %s,
                    pgp_sym_encrypt(med, %s),
                    pgp_sym_encrypt(amt, %s),
                    pgp_sym_encrypt(schd, %s)
                FROM unnest(%s, %s, %s) AS t(med, amt, schd)"""
        params = (
            admissionID,
            encryptionKey,
            encryptionKey,
            encryptionKey,
            [prescription['name'] for prescription in prescriptions],
            [prescription['amount'] for prescription in prescriptions],
            [prescription['schedule'] for prescription in prescriptions],
        )
        cursor.execute(sql, params)
        
def insertNotes(admissionID, notes, encryptionKey, fixedSalt):
    with hospitalDB.get_cursor() as cursor:
        sql = """INSERT INTO PatientNote (admission_id, author_id, note_type, note_text, note_datetime)
                SELECT
                    %s,
                    (SELECT user_id FROM Staff WHERE username_hash = encode(digest(author || %s, 'sha256'), 'hex')),
                    type,
                    pgp_sym_encrypt(text, %s),
                    pgp_sym_encrypt(dt, %s)
                FROM unnest(%s, %s, %s, %s) AS t(author, type, text, dt)"""
        params =(
            admissionID,
            fixedSalt,
            encryptionKey,
            encryptionKey,
            [note['author'] for note in notes],
            [note['type'] for note in notes],
            [note['text'] for note in notes],
            [note['time'].isoformat() for note in notes]
        )
        cursor.execute(sql, params)
        
def insertProcedures(admissionID, procedures, encryptionKey):

    with hospitalDB.get_cursor() as cursor:
        sql = """INSERT INTO ScheduledProcedure (admission_id, procedure_name, scheduled_datetime)
                SELECT
                    %s,
                    pgp_sym_encrypt(proc, %s),
                    pgp_sym_encrypt(dt, %s)
                FROM unnest(%s, %s) AS t(proc, dt)"""
        params = (
            # Procedures
            admissionID,
            encryptionKey,
            encryptionKey,
            [procedure['name'] for procedure in procedures],
            [procedure['date'] for procedure in procedures],
        )
        cursor.execute(sql, params)
        
def insertBill(admissionID, billingTotal, billingPaid, billingInsurance, itemizedBill):
    with hospitalDB.get_cursor() as cursor:
        sql = """WITH
        billing AS (
                INSERT INTO Billing (admission_id, total_amount_owed, total_amount_paid, insurance_paid)
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING billing_id
            ),
            billing_details AS (
                INSERT INTO BillingDetail (billing_id, item_description, charge_amount)
                SELECT
                    (SELECT billing_id FROM billing),
                    item_desc,
                    amt
                FROM unnest(%s, %s) AS t(item_desc, amt)
            )
            SELECT 1;"""
        params = (
            # Billing
            admissionID,
            billingTotal,
            billingPaid,
            billingInsurance,
                
            # Billing details
            [item['name'] for item in itemizedBill],
            [item['cost'] for item in itemizedBill]
        )
        cursor.execute(sql, params)
        
hospitalDB.run()
fake = Faker()


# Configure for realistic medical data
Faker.seed(42)
random.seed(42)

# --- Helper Functions ---
def generate_phone():
    return f"{fake.random_int(100, 999)}-{fake.random_int(100, 999)}-{fake.random_int(1000, 9999)}"

def generate_prescription():
    meds = ["Aspirin", "Metformin", "Lisinopril", "Amoxicillin", "Omeprazole"]
    return {
        "name": random.choice(meds),
        "amount": f"{random.randint(1, 500)}mg",
        "schedule": random.choice(["Daily", "BID", "TID", "QID"])
    }

def generate_procedure():
    procedures = ["X-Ray", "MRI", "Blood Test", "Echocardiogram", "Colonoscopy"]
    return {
        "name": random.choice(procedures),
        "date": str(fake.date_between(start_date="+1d", end_date="+30d"))
    }

# --- Populate Tables ---

def populate_users( encryptionKey, fixedSalt, n=50):
    types = ['Administrator', 'Medical Personnel', 'Volunteer', 'Office Staff', 'Physician']

    for _ in range(n):
        user_type = random.choice(types)
        username = fake.unique.user_name()
        password = fake.password()
        insertStaff(fake.first_name(), fake.last_name(), username, password, user_type, encryptionKey, fixedSalt)
        InsertData.log_action(f'Added Staff To System Username: {username}')
        

def populate_patients(encryptionKey, fixedSalt, n=100):
    sql = """SELECT pgp_sym_decrypt(username, %s) FROM Staff WHERE type_id = 5"""
    params = (encryptionKey,)
    with hospitalDB.get_cursor() as cursor:
        cursor.execute(sql, params)
        doctor_ids = [row[0] for row in cursor.fetchall()]
    insurances = ['Progressive', 'United Healthcare', 'Allstate', 'Local Provider']
    
    for _ in range(n):
        fname = fake.first_name()
        lname = fake.last_name()
        insertPatient(lname, fname, fake.first_name() if random.random() < 0.3 else None, fake.address(), generate_phone(), generate_phone(), generate_phone(), fake.first_name() + ' ' + fake.last_name(), generate_phone(), fake.first_name() + ' ' + fake.last_name(), generate_phone(), random.choice(doctor_ids), random.choice(insurances), str(fake.random_int(10000, 99999)), str(fake.random_int(10000, 99999)), keys[0], keys[1])
        InsertData.log_action(f'Added Patient To System: {fname} {lname}')

def populate_admissions(encryptionKey, fixedSalt, n=200):
    with hospitalDB.get_cursor() as cursor:
        cursor.execute("SELECT patient_id FROM Patient")
        patient_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT user_id FROM Staff WHERE type_id = 5")
        doctor_ids = [row[0] for row in cursor.fetchall()]
    for _ in range(n):
        admit_date = fake.date_between(start_date="-2y", end_date="today")
        id = random.choice(patient_ids)
        with hospitalDB.get_cursor() as cursor:
            cursor.execute(""" UPDATE admission
                                SET discharge_datetime = pgp_sym_encrypt(CURRENT_TIMESTAMP::text, %s)
                                WHERE patient_id = %s
                                AND discharge_datetime IS NULL;""", (encryptionKey, id))
        
        discharge_date = None
        facilities = ["Main Hospital", "North Clinic", "South Clinic"]
        admissionID = insertAdmission(id, str(admit_date), fake.sentence(nb_words=6), discharge_date, random.choice(facilities), random.randint(1, 10), fake.random_int(100, 999), fake.random_int(1, 50), random.choice(doctor_ids), keys[0])
        InsertData.log_action(f'Added Admission To System PatientID: {id}')
        # Add Approved Visitors (0 - 5, Any)
        visitors = []
        for _ in range(random.randint(1, 5)):
            visitors.append(fake.first_name() + ' ' + fake.last_name())
        InsertData.insertVisitors(admissionID, visitors, encryptionKey)
        InsertData.log_action(f'Added Visitors To Admission ID: {admissionID}')
        # Add prescriptions (1-3 per admission)
        prescriptions = []
        for _ in range(random.randint(1, 3)):
            rx = generate_prescription()
            prescriptions.append(rx)
        insertPrescriptions(admissionID, prescriptions, encryptionKey)
        InsertData.log_action(f'Added Presciptions To Admission ID: {admissionID}')

        # Add notes (2-5 per admission)
        sql = "SELECT pgp_sym_decrypt(username, %s) FROM Staff WHERE type_id IN (2, 5)"
        params = (encryptionKey,)
        with hospitalDB.get_cursor() as cursor:
            cursor.execute(sql, params)
            staff_ids = [row[0] for row in cursor.fetchall()]
        notes = []
        for _ in range(random.randint(2, 5)):
            note = {'author': random.choice(staff_ids), 'type': random.choice(["Doctor", "Nurse"]), 'text': fake.paragraph(nb_sentences=3), 'time' : fake.date_time_between(start_date=admit_date, end_date=discharge_date or datetime.now())}
            notes.append(note)
        insertNotes(admissionID, notes, encryptionKey, fixedSalt)
        InsertData.log_action(f'Added Notes To Admission ID: {admissionID}')

        # Add procedures (0-2 per admission)
        procedures = []
        for _ in range(random.randint(0, 2)):
            proc = generate_procedure()
            procedures.append(proc)
        if len(procedures) > 0:
            insertProcedures(admissionID, procedures, encryptionKey)
            InsertData.log_action(f'Added Procedures To Admission ID: {admissionID}')
        # Add billing
        total_owed = Decimal(random.randint(1000, 100000))
        total_paid = total_owed * Decimal(random.uniform(0.1, 0.9))
        insurance_paid = total_owed - total_paid
        items = ["Room Charge", "Lab Fee", "Medication", "Surgery Fee", "Consultation"]
        # Add billing details (3-10 items)
        itemlist = []
        for _ in range(random.randint(3, 10)):
            item = {'name': random.choice(items), 'cost': float(random.randint(50, 5000))}
            itemlist.append(item)
        InsertData.insertBill(admissionID, total_owed, total_paid, insurance_paid, itemlist)
        if random.random() < 0.7:
            UpdateDB.admissionUpdateDischarge(admissionID, admit_date + timedelta(days=random.randint(1, 30)), encryptionKey)

# --- Execute Data Generation ---
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    hospitalDB.userLogin('DataGen', 'qwertyuiop', keys[1])
    populate_users(keys[0], keys[1], 100)          # 50 users
    populate_patients(keys[0], keys[1], 200)      # 200 patients
    populate_admissions(keys[0], keys[1], 250)    # 250 admissions
    print("Dummy data generation complete!")