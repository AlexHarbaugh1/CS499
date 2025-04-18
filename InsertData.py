import hospitalDB
import psycopg2
import EncryptionKey
import hashlib
import datetime

def generatePrefixes(text):
    return [text[:i] for i in range(1, len(text) + 1)]
def hashPrefix(prefix, fixedSalt):
    return hashlib.sha256((prefix + fixedSalt).encode()).hexdigest()

def insertStaff(fname, lname, username, password, type, fixedSalt):
    type_map = {
        "Administrator": 1,
        "Medical Personnel": 2, 
        "Office Staff": 3,
        "Volunteer": 4,
        "Physician": 5
    }
    typeID = type_map.get(type)

    with hospitalDB.get_cursor() as cursor:    
        fnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(fname)]
        lnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(lname)]
        sql = """UPDATE staffwriteview
                    SET
                    first_name = %s,
                    last_name = %s,
                    first_name_prefix_trgms= %s,
                    last_name_prefix_trgms= %s,
                    username = %s,
                    password = %s,
                    type_id = %s;"""
        params = (
            fname,
            lname,
            fnameHashedPrefixes,
            lnameHashedPrefixes,
            username,
            password,
            typeID
        )
        try:
            cursor.execute(sql, params)
        except psycopg2.ProgrammingError as e:
            print("Error: Insufficient privileges to execute this operation")
        finally:
            cursor.close()

def insertPatient(fname, mname, lname, address, doctorID, fixedSalt):
    fnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(fname)]
    if mname != None:
        mnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(mname)]
    else:
        mnameHashedPrefixes = None
    lnameHashedPrefixes = [hashPrefix(prefix, fixedSalt) for prefix in generatePrefixes(lname)]
    with  hospitalDB.get_cursor() as cursor:
        sql = """UPDATE patientwriteview
        SET
        first_name = %s,
        middle_name= %s,
        last_name= %s,
        first_name_prefix_trgms= %s,
        middle_name_prefix_trgms= %s,
        last_name_prefix_trgms= %s,
        mailing_address= %s,
        family_doctor_id = %s;"""
 
        params = (
            fname,
            mname,
            lname,
            fnameHashedPrefixes,
            mnameHashedPrefixes,
            lnameHashedPrefixes,
            address,
            doctorID
        )
        try:
            cursor.execute(sql, params)
        except psycopg2.ProgrammingError as e:
            print("Error: Insufficient privileges to execute this operation")
        finally:
            cursor.close()

def insertAdmission(patientID, locationID, doctorID, admissionDateTime, admissionReason):
    with hospitalDB.get_cursor() as cursor:
        sql = """UPDATE admissionwriteview
                SET
                location_id = %s,
                doctor_id = %s,
                admittance_datetime = %s,
                reason_for_admission = %s
                WHERE patient_id = %s;
                """
        params = (
            locationID,
            doctorID,
            admissionDateTime,
            admissionReason,
            patientID
        )
        cursor.execute(sql, params)
        cursor.close()
    

def insertLocation(facility, floor, room, bed):
    with hospitalDB.get_cursor() as cursor:
            sql = """UPDATE locationwriteview
                    SET
                    facility = %s,
                    floor = %s,
                    room = %s,
                    bed = %s;
                    """
            params = (
                facility,
                floor,
                room,
                bed
            )
            cursor.execute(sql, params)
            cursor.close()
    
def insertVisitors(admissionID, visitorNames, encryptionKey):
    with  hospitalDB.get_cursor() as cursor:
        encryptedNames = []
        for name in visitorNames:
            sql = "SELECT pgp_sym_encrypt(%s, %s) AS encrypted_name;"
            params = (name, encryptionKey)
            cursor.execute(sql, params)
            encryptedNames.append(cursor.fetchone()[0])
        sql = """UPDATE visitorwriteview
                SET
                visitors = %s
                WHERE admission_id = %s;"""
        params = (
            encryptedNames,
            admissionID
        )
        cursor.execute(sql, params)
        cursor.close()

def insertPrescription(admissionID, name, amount, schedule):
    usertype = hospitalDB.getCurrentUserType()
    if (usertype == 'Physician' or 'Administrator'):
        sql = """UPDATE PhysicianWriteView
                SET
                medication_name = %s,
                medication_amount = %s,
                medication_schedule = %s
                WHERE admission_id = %s;"""
        with  hospitalDB.get_cursor() as cursor:
            
            params = (
                name,
                amount,
                schedule,
                admissionID
            )
            cursor.execute(sql, params)
            cursor.close()
    else: 
        print("Permission Denied")

def insertNote(admissionID, noteText):
    usertype = hospitalDB.getCurrentUserType()
    if (usertype == 'Physician' or 'Administrator'):
        sql = """UPDATE PhysicianWriteView
                SET
                note_text = %s
                WHERE admission_id = %s;"""
    else:
        sql = """UPDATE NurseWriteView
                SET
                note_text = %s
                WHERE admission_id = %s;"""
    with  hospitalDB.get_cursor() as cursor:
        
        params = (
            noteText,
            admissionID
        )
        cursor.execute(sql, params)
        cursor.close()

def insertProcedure(admissionID, procedureName, procedureSchedule):
    sql = """UPDATE PhysicianWriteView
                SET
                procedure_name = %s,
                procedure_schedule = %s
                WHERE admission_id = %s;"""
    params = (
        procedureName,
        procedureSchedule,
        admissionID
        )
    with hospitalDB.get_cursor() as cursor:
        cursor.execute(sql, params)

def insertBill(admissionID, billingTotal, billingPaid, billingInsurance, itemizedBill):
    with  hospitalDB.get_cursor() as cursor:
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
        cursor.close()

    # Test Input data
    # Uncomment desired function to test
    # Must have ran all functions above it for the next one to work

def insertBilledItem(admissionID, itemName, itemCost):
    with hospitalDB.get_cursor() as cursor:
        sql = """UPDATE billwriteview
                SET
                    billed_item_name = %s,
                    billed_item_cost = %s
                WHERE admission_id = %s"""
        params = (
                  itemName,
                  itemCost,
                  admissionID
                  )
        cursor.execute(sql, params)
        

if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    hospitalDB.run()
    #hospitalDB.userLogin('Physician1', 'qwertyuiop', keys[1])
    insertStaff('Volunteer', 'One', 'Volunteer1', 'qwertyuiop', 'Volunteer', keys[1])
    insertStaff('MedicalPersonnel', 'One', 'MedicalPersonnel1', 'qwertyuiop', 'Medical Personnel', keys[1])
    insertStaff('Physician', 'One', 'Physician1', 'qwertyuiop', 'Physician', keys[1])
    insertStaff('OfficeStaff', 'One', 'OfficeStaff1', 'qwertyuiop', 'Office Staff', keys[1])
    insertStaff('Administrator', 'One', 'Administrator1', 'qwertyuiop', 'Administrator', keys[1])
    #insertPatient('Elliot', 'P', 'Cyrus', 'The Moon', '3', keys[1])
    #insertLocation('Main Ward', '1', '101', '1')
    #insertAdmission('201', '1', '3', datetime.datetime.now(), 'Needs Halp')
    #insertVisitors('16', ['Mitch', 'Taylor', 'Josh'], keys[0])
    #insertNote('16', 'The Meth really showed results')
    #insertProcedure('16', 'Finger Surgery', '2025-03-15 12:00:00')
    #insertBill(admissionID, '200000', '170000', '30000', [{'name': 'ER Visit', 'cost': float('75.27')}, {'name': 'X-Ray', 'cost': float('4000')}, {'name': 'Ibuprofen', 'cost': float('5.73')}, {'name': 'Morphine', 'cost': float('70919')}, {'name': 'Meth', 'cost': float('100000')}, {'name': 'Finger Surgery', 'cost': float('25000')}])