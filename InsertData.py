import psycopg2

def insertStaff(cursor, fname , lname, username, password, type, encryptionkey, fixed_salt):
    cursor.execute(f"""INSERT INTO Staff (first_name, last_name, username_hash, username, password_hash, type_id)
                   Values(
                   pgp_sym_encrypt('{fname}', '{encryptionkey}'),
                   pgp_sym_encrypt('{lname}', '{encryptionkey}'),
                   encode(digest('{username}' || '{fixed_salt}', 'sha256'), 'hex'),
                   pgp_sym_encrypt('{username}', '{encryptionkey}'),
                   crypt('{password}', gen_salt('bf')),
                   (SELECT type_id FROM UserType WHERE type_name = '{type}'));""")

def insertPatient(cursor, lname, fname, mname, address, hPhone, mPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum, encryptionkey, fixed_salt):
    sql = """WITH
    doctor AS (
        SELECT user_id 
        FROM Staff 
        WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex')
    ),
    new_patient AS (
        INSERT INTO Patient (first_name, last_name, middle_name, mailing_address, family_doctor_id)
        VALUES (
            pgp_sym_encrypt(%s, %s),
            pgp_sym_encrypt(%s, %s),
            pgp_sym_encrypt(%s, %s),
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
        doctor, fixed_salt,
        
        # new_patient
        fname, encryptionkey,
        mname, encryptionkey,
        lname, encryptionkey,
        address, encryptionkey,
        
        # phone_numbers
        hPhone, encryptionkey,
        mPhone, encryptionkey,
        wPhone, encryptionkey,
        
        # emergency_contacts
        c1Name, encryptionkey,
        c1Phone, encryptionkey,
        c2Name, encryptionkey,
        c2Phone, encryptionkey,
        
        # new_insurance
        insCarrier, encryptionkey,
        insAcc, encryptionkey,
        insGNum, encryptionkey
    )

    cursor.execute(sql, params)

def insertAdmission():
    print("Hi")