from hospitalDB import getConnection
from InsertData import hashPrefix, generatePrefixes
import EncryptionKey

def patientUpdateFirstName(patientID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    newNameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newName)]
    sql = """UPDATE Patient
            SET first_name = pgp_sym_encrypt(%s, %s),
            first_name_prefix_trgms = %s
            WHERE patient_id = %s;"""
    params = (
        newName, encryptionKey,
        newNameHashedPrefixes,
        patientID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateMiddleName(patientID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    newNameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newName)]
    sql = """UPDATE Patient
            SET middle_name = pgp_sym_encrypt(%s, %s),
            middle_name_prefix_trgms = %s
            WHERE patient_id = %s;"""
    params = (
        newName, encryptionKey,
        newNameHashedPrefixes,
        patientID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateLastName(patientID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    newNameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newName)]
    sql = """UPDATE Patient
            SET last_name = pgp_sym_encrypt(%s, %s),
            last_name_prefix_trgms = %s
            WHERE patient_id = %s;"""
    params = (
        newName, encryptionKey,
        newNameHashedPrefixes,
        patientID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateAddress(patientID, newAddress, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """UPDATE Patient
            SET mailing_address = pgp_sym_encrypt(%s, %s)
            WHERE patient_id = %s;"""
    params = (
        newAddress, encryptionKey,
        patientID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdatePhone(patientID, phoneType, PhoneNumber, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """UPDATE phonenumber
            SET phone_number = pgp_sym_encrypt(%s, %s)
            WHERE patient_id = %s AND phone_type = %s;"""
    params = (
        PhoneNumber, encryptionKey,
        patientID, phoneType
    )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateFamilyDoctor(patientID, newDoctor):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """UPDATE Patient
            SET family_doctor_id = %s
            WHERE patient_id = %s;"""
    params = (
        newDoctor,
        patientID
    )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateInsurance(patientID, newCarrierName, newAccNum, newGroupNum, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """Update Insurance
    SET carrier_name = pgp_sym_encrypt(%s, %s),
    account_number = pgp_sym_encrypt(%s, %s),
    group_number = pgp_sym_encrypt(%s, %s)
    WHERE patient_id = %s;"""
    params = (
        newCarrierName, encryptionKey,
        newAccNum, encryptionKey,
        newGroupNum, encryptionKey,
        patientID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def patientUpdateContact(patientID, newContactName, newContactNumber, contactOrder, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """UPDATE EmergencyContact
            SET contact_name = pgp_sym_encrypt(%s, %s),
            contact_phone = pgp_sym_encrypt(%s, %s)
            WHERE patient_id = %s AND contact_order = %s;"""
    params = (
        newContactName, encryptionKey,
        newContactNumber, encryptionKey,
        patientID, contactOrder
    )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def staffUpdateFirstName(userID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    newNameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newName)]
    sql = """UPDATE Staff
            SET first_name = pgp_sym_encrypt(%s, %s),
            first_name_prefix_trgms = %s
            WHERE user_id = %s;"""
    params = (
        newName, encryptionKey,
        newNameHashedPrefixes,
        userID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def staffUpdateLastName(userID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    newNameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newName)]
    sql = """UPDATE Staff
            SET last_name = pgp_sym_encrypt(%s, %s),
            last_name_prefix_trgms = %s
            WHERE user_id = %s;"""
    params = (
        newName, encryptionKey,
        newNameHashedPrefixes,
        userID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def staffUpdateUsername(userID, newName, encryptionKey, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """UPDATE Staff
            SET username = pgp_sym_encrypt(%s, %s),
            username_hash = encode(digest(%s || %s, 'sha256'), 'hex') 
            WHERE user_id = %s;"""
    params = (
        newName, encryptionKey,
        newName, fixedSalt,
        userID
        )
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def staffUpdateType(userID, newType):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """Update Staff
            SET type_id = (SELECT type_id FROM usertype where type_name = %s)
            WHERE user_id = %s"""
    params = (
        newType,
        userID)
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    #patientUpdateFirstName('81', 'Alexa', keys[0], keys[1])
    #patientUpdateMiddleName('81', 'Ellen', keys[0], keys[1])
    #patientUpdateLastName('81', 'Montraeu', keys[0], keys[1])
    #patientUpdateAddress('81', '1234 Main Street, Huntsville, AL 35850', keys[0])
    #patientUpdateFamilyDoctor('81', '19')
    #patientUpdateInsurance('81', 'United Healthcare', '23523', '63456', keys[0])
    #patientUpdateContact('71', 'Alex Harbaugh', '123-456-7890', 1, keys[0])
    #patientUpdatePhone('2', 'Home', '123-456-7890', keys[0])
    #staffUpdateFirstName('1', 'Johnny', keys[0], keys[1])
    #staffUpdateLastName('1', 'Johnson', keys[0], keys[1])
    #staffUpdateUsername('1', 'JohnSquared', keys[0], keys[1])
    staffUpdateType('1','Physician')