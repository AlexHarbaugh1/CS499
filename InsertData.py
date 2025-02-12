import psycopg2
import EncryptionKey
import os
from dotenv import load_dotenv
def insertStaff(cursor, fname , lname, username, password, type):
    load_dotenv()
    fixed_salt = os.getenv("fixed_salt")
    keys = EncryptionKey.getKeys()
    cursor.execute(f"""INSERT INTO Staff (first_name, last_name, username_hash, username, password_hash, type_id)
                   Values(
                   pgp_sym_encrypt('{fname}', '{keys[0]}'),
                   pgp_sym_encrypt('{lname}', '{keys[1]}'),
                   encode(digest('{username}' || '{fixed_salt}', 'sha256'), 'hex'),
                   pgp_sym_encrypt('{username}', '{keys[2]}'),
                   crypt('{password}', gen_salt('bf')),
                   (SELECT type_id FROM UserType WHERE type_name = '{type}'));""")

def insertPatient(cursor, lname, fname, mname, address, hPhone, mPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum):
    load_dotenv()
    fixed_salt = os.getenv("fixed_salt")
    keys = EncryptionKey.getKeys()
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
        VALUES (
            ((SELECT patient_id FROM new_patient), 'Home', pgp_sym_encrypt(%s, %s)),
            ((SELECT patient_id FROM new_patient), 'Mobile', pgp_sym_encrypt(%s, %s)),
            ((SELECT patient_id FROM new_patient), 'Work', pgp_sym_encrypt(%s, %s))
        )
    ),
    emergency_contacts AS (
        INSERT INTO EmergencyContact (patient_id, contact_name, contact_phone, contact_order)
        VALUES(
            ((SELECT patient_id FROM new_patient), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), 1),
            ((SELECT patient_id FROM new_patient), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), 2)
        )
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
        fname, keys[3],
        lname, keys[4],
        mname, keys[5],
        address, keys[6],
        
        # phone_numbers
        hPhone, keys[7],
        mPhone, keys[8],
        wPhone, keys[9],
        
        # emergency_contacts
        c1Name, keys[0],
        c1Phone, keys[1],
        c2Name, keys[2],
        c2Phone, keys[3],
        
        # new_insurance
        insCarrier, keys[4],
        insAcc, keys[5],
        insGNum, keys[6]
    )

    cursor.execute(sql, params)

def insertPrescription():
    print("hi")
def insertAdmission():
    print("Hi")