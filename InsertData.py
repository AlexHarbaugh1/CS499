from hospitalDB import getConnection
import EncryptionKey
import SearchDB
import hashlib
def generatePrefixes(text):
    return [text[:i] for i in range(1, len(text) + 1)]
def hashPrefix(prefix, fixedSalt):
    return hashlib.sha256((prefix + fixedSalt).encode()).hexdigest()

def insertStaff(fname , lname, username, password, type, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    fnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(fname)]
    lnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(lname)]
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
    conn.commit()
    cursor.close()
    conn.close()

def insertPatient(lname, fname, mname, address, hPhone, mPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    fnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(fname)]
    if mname != None:
        mnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(mname)]
    else:
        mnameHashedPrefixes = None
    lnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(lname)]

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
    conn.commit()
    cursor.close()
    conn.close()

def insertAdmission(fName, mName, lName, admissionDateTime, admissionReason, releaseDateTime,
                    hospitalFacility, hospitalFloor, hospitalRoom, hospitalBed, doctorID, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    patient_id = SearchDB.searchPatientWithName(fName, mName, lName, encryptionKey, fixedSalt)[0][0]
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
        patient_id,
        doctorID,
        admissionDateTime, encryptionKey,
        admissionReason, encryptionKey,
        releaseDateTime if releaseDateTime else None, encryptionKey,

        
        )
    cursor.execute(sql, params)
    conn.commit()
    ID = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return ID

def insertPrescriptions(admissionID, prescriptions, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

def insertNotes(admissionID, notes, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

def insertProcedures(admissionID, procedures, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

def insertBill(admissionID, billingTotal, billingPaid, billingInsurance, itemizedBill):
    conn = getConnection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

    # Test Input data
    # Uncomment desired function to test
    # Must have ran all functions above it for the next one to work
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    insertStaff('Blair', 'Stafford', 'BlairStafford', 'qwertyuiop', 'Medical Personnel', keys[0], keys[1])
    #insertPatient('Logos', 'William', 'Graves', '601 John Wright DR NW', '1111111111', '2222222222', '3333333333', 'Mitch', '4444444444', 'Taylor', '5555555555', 'BlairStafford', 'United Healthcare', '12345', '54321', keys[0], keys[1])
    #print(insertAdmission('William', 'Graves', 'Logos', '2025-03-02 11:11:00', 'Fingy Broked', '2025-02-03 01:12:00', 'ER', '1', '123', '1', keys[0], keys[1]))
    #insertPrescriptions([{'name': 'Ibuprofen', 'amount': '500mg', 'schedule': 'Once Every Six Hours'}, {'name': 'Morphine', 'amount': 'A lot', 'schedule': 'Once, he would not stop screaming'}, {'name': 'Crystal Meth', 'amount': 'One Teenth', 'schedule': 'Twice Daily'}], keys[0])
    #insertNotes([{'author': 'BlairStafford', 'type': 'Doctor', 'text': 'The Meth really showed results', 'time' : datetime.datetime.now()}, {'author': 'BlairStafford', 'type': 'Nurse', 'text': 'I think Dr. Blair needs to be fired.', 'time' : datetime.datetime.now()}], keys[0], keys[1])
    #insertProcedures([{'name': 'Finger Surgery', 'date': '2025-03-15 12:00:00'}], keys[0])
    #insertBill('200000', '170000', '30000', [{'name': 'ER Visit', 'cost': float('75.27')}, {'name': 'X-Ray', 'cost': float('4000')}, {'name': 'Ibuprofen', 'cost': float('5.73')}, {'name': 'Morphine', 'cost': float('70919')}, {'name': 'Meth', 'cost': float('100000')}, {'name': 'Finger Surgery', 'cost': float('25000')}])