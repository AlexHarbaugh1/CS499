from hospitalDB import get_cursor
from InsertData import hashPrefix, generatePrefixes
from SearchDB import passwordMatch
import EncryptionKey
import datetime

def patientUpdateFirstName(patientID, newName, encryptionKey, fixedSalt):

    with get_cursor() as cursor:
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
        cursor.close()

def patientUpdateMiddleName(patientID, newName, encryptionKey, fixedSalt):
    with get_cursor() as cursor:
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
        cursor.close()

def patientUpdateLastName(patientID, newName, encryptionKey, fixedSalt):
    with get_cursor() as cursor:
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
        cursor.close()

def patientUpdateAddress(patientID, newAddress, encryptionKey):
    with get_cursor() as cursor:
        sql = """UPDATE Patient
                SET mailing_address = pgp_sym_encrypt(%s, %s)
                WHERE patient_id = %s;"""
        params = (
            newAddress, encryptionKey,
            patientID
            )
        cursor.execute(sql, params)
        cursor.close()

def patientUpdatePhone(patientID, phoneType, PhoneNumber, encryptionKey):
    with get_cursor() as cursor:
        sql = """UPDATE phonenumber
                SET phone_number = pgp_sym_encrypt(%s, %s)
                WHERE patient_id = %s AND phone_type = %s;"""
        params = (
            PhoneNumber, encryptionKey,
            patientID, phoneType
        )
        cursor.execute(sql, params)
        cursor.close()

def patientUpdateFamilyDoctor(patientID, newDoctor):
    with get_cursor() as cursor:
        sql = """UPDATE Patient
                SET family_doctor_id = %s
                WHERE patient_id = %s;"""
        params = (
            newDoctor,
            patientID
        )
        cursor.execute(sql, params)
        cursor.close()

def patientUpdateInsurance(patientID, newCarrierName, newAccNum, newGroupNum, encryptionKey):
    with get_cursor() as cursor:
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
        cursor.close()

def patientUpdateContact(patientID, newContactName, newContactNumber, contactOrder, encryptionKey):
    with get_cursor() as cursor:
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
        cursor.close()

def staffUpdateFirstName(userID, newName, encryptionKey, fixedSalt):
    with get_cursor() as cursor:
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
        cursor.close()

def staffUpdateLastName(userID, newName, encryptionKey, fixedSalt):
    with get_cursor() as cursor:
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
        cursor.close()

def staffUpdateUsername(userID, newName, encryptionKey, fixedSalt):
    with get_cursor() as cursor:
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
        cursor.close()

def staffUpdatePassword(userID, newPassword, oldPassword):
    with get_cursor() as cursor:
        if (passwordMatch(userID, oldPassword)):
            sql = """UPDATE Staff
                    SET password_hash = crypt(%s, gen_salt('bf'))
                    WHERE user_id = %s;"""
            params = (
                newPassword,
                userID
                )
        cursor.execute(sql, params)
        cursor.close()

def staffUpdateType(userID, newType):
    with get_cursor() as cursor:
        sql = """Update Staff
                SET type_id = (SELECT type_id FROM usertype where type_name = %s)
                WHERE user_id = %s"""
        params = (
            newType,
            userID)
        cursor.execute(sql, params)
        cursor.close()

def admissionUpdateDischarge(admissionID, dischargeTime, encryptionkey):
    with get_cursor() as cursor:
        sql = """UPDATE admission
                SET discharge_datetime = pgp_sym_encrypt(%s, %s)
                WHERE admission_id = %s;"""
        params = (
            str(dischargeTime), encryptionkey,
            admissionID)
        cursor.execute(sql, params)
        cursor.close()
        
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
    #staffUpdateType('1','Physician')
    #staffUpdatePassword('51', 'BlairStafford', 'poiuytrewq', 'qwertyuiop', keys[1])
    admissionUpdateDischarge('1', datetime.datetime.now(), keys[0])