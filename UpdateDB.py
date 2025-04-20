from hospitalDB import get_cursor, getCurrentUserType, userLogin
from InsertData import hashPrefix, generatePrefixes, log_action
from SearchDB import passwordMatch
import psycopg2
import EncryptionKey
import datetime
def updatePrefixTrigrams(patientID, field, newValue, fixedSalt):

    if newValue is None:
        return False
        
    newValueHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(newValue)]

    trigram_field_map = {
        'fname': 'first_name_prefix_trgms',
        'mname': 'middle_name_prefix_trgms',
        'lname': 'last_name_prefix_trgms'
    }
    
    if field not in trigram_field_map:
        print(f"Invalid field name: {field}")
        return False
    
    trigram_field = trigram_field_map[field]
    
    with get_cursor() as cursor:
        current_role = getCurrentUserType()
        cursor.execute("SET ROLE postgres")
        sql = f"""UPDATE Patient
                SET
                {trigram_field} = %s
                WHERE patient_id = %s;"""
        params = (
            newValueHashedPrefixes,
            patientID
        )
        
        try:
            cursor.execute(sql, params)
            role = current_role.lower().replace(" ", "") + "_role"
            sql = """SET ROLE %s;"""
            params = (role,)
            cursor.execute(sql, params)
            return True
        except psycopg2.Error as e:
            print(f"Error updating {field}: {e}")
            return False

def patientUpdateFirstName(patientID, newName, fixedSalt):

    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET first_name = %s
                WHERE patient_id = %s;"""
        params = (
            newName,
            patientID
            )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} First Name")
        updatePrefixTrigrams(patientID, 'fname', newName, fixedSalt)
        
def patientUpdateMiddleName(patientID, newName, fixedSalt):
    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET middle_name = %s
                WHERE patient_id = %s;"""
        params = (
            newName,
            patientID
            )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} Middle Name")
        updatePrefixTrigrams(patientID, 'mname', newName, fixedSalt)

def patientUpdateLastName(patientID, newName, fixedSalt):
    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET last_name = %s
                WHERE patient_id = %s;"""
        params = (
            newName,
            patientID
            )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} Last Name")
        updatePrefixTrigrams(patientID, 'lname', newName, fixedSalt)

def patientUpdateAddress(patientID, newAddress):
    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET mailing_address = %s
                WHERE patient_id = %s;"""
        params = (
            newAddress,
            patientID
            )
        cursor.execute(sql, params)
        
def patientUpdatePhone(patientID, phoneType, PhoneNumber):
    with get_cursor() as cursor:
        pType = phoneType.lower() + "_phone"
        sql = """UPDATE officestaffview
                SET home_phone = CASE WHEN %s = 'home_phone' THEN %s ELSE home_phone END,
                work_phone = CASE WHEN %s = 'work_phone' THEN %s ELSE work_phone END,
                mobile_phone = CASE WHEN %s = 'mobile_phone' THEN %s ELSE mobile_phone END
                WHERE patient_id = %s;"""
        
        params = (
            pType, PhoneNumber,
            pType, PhoneNumber,
            pType, PhoneNumber,
            patientID
        )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} Phone Number")       

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
        
def patientUpdateInsurance(patientID, newCarrierName, newAccNum, newGroupNum):
    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET insurance_carrier = %s,
                insurance_account = %s,
                insurance_group = %s
                WHERE patient_id = %s;"""
        params = (
            newCarrierName,
            newAccNum,
            newGroupNum,
            patientID
            )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} Insurance")
        
def patientUpdateContact(patientID, newContactName, newContactNumber, contactOrder):
    with get_cursor() as cursor:
        sql = """UPDATE officestaffview
                SET ec1_name = CASE WHEN %s = '1' THEN %s ELSE ec1_name END,
                ec1_phone = CASE WHEN %s = '1' THEN %s ELSE ec1_phone END,
                ec2_name = CASE WHEN %s = '2' THEN %s ELSE ec2_name END,
                ec2_phone = CASE WHEN %s = '2' THEN %s ELSE ec2_phone END
                WHERE patient_id = %s;"""
        params = (
            contactOrder, newContactName,
            contactOrder, newContactNumber,
            contactOrder, newContactName,
            contactOrder, newContactNumber,
            patientID
        )
        cursor.execute(sql, params)
        log_action(f"Update Patient ID: {patientID} Emergency Contact")
        
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
        
def staffUpdateType(userID, newType):
    with get_cursor() as cursor:
        sql = """Update Staff
                SET type_id = (SELECT type_id FROM usertype where type_name = %s)
                WHERE user_id = %s"""
        params = (
            newType,
            userID)
        cursor.execute(sql, params)
        
def admissionUpdateDischarge(admissionID, dischargeTime, encryptionkey):
    with get_cursor() as cursor:
        sql = """UPDATE admission
                SET discharge_datetime = pgp_sym_encrypt(%s, %s)
                WHERE admission_id = %s;"""
        params = (
            str(dischargeTime), encryptionkey,
            admissionID)
        cursor.execute(sql, params)
        log_action(f"Discharge Admission ID: {admissionID}")
        
        
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    
    #patientUpdateFamilyDoctor('81', '19')
    #patientUpdateInsurance('81', 'United Healthcare', '23523', '63456', keys[0])
    #patientUpdateContact('71', 'Alex Harbaugh', '123-456-7890', 1, keys[0])
    #patientUpdatePhone('2', 'Home', '123-456-7890', keys[0])
    #staffUpdateFirstName('1', 'Johnny', keys[0], keys[1])
    #staffUpdateLastName('1', 'Johnson', keys[0], keys[1])
    #staffUpdateUsername('1', 'JohnSquared', keys[0], keys[1])
    #staffUpdateType('1','Physician')
    #staffUpdatePassword('51', 'BlairStafford', 'poiuytrewq', 'qwertyuiop', keys[1])
    userLogin('OfficeStaff1', 'qwertyuiop', keys[1])
    patientUpdateFirstName('202', 'Blair', keys[1])
    patientUpdateMiddleName('202', 'Gaming', keys[1])
    patientUpdateLastName('202', 'Stafford', keys[1])
    patientUpdateAddress('202', '1234 Main Street, Huntsville, AL 35850')
    #admissionUpdateDischarge('1', datetime.datetime.now(), keys[0])