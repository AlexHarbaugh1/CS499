from hospitalDB import getConnection
import EncryptionKey
# passwordMatch checks if the entered password is the same as the saved password
# Return TRUE or FALSE
def passwordMatch(username, password, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT (password_hash = crypt(%s, password_hash)) AS password_match
    FROM Staff WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex');"""
    
    params = (
        password,
        username, fixedSalt
    )
    cursor.execute(sql, params)
    match = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return(match)
# searchPatientWithName takes the names as input and searches for the patient in the database
# The function automatically chooses which SQL to execute based on the given parameters
# i.e. missing names
# leave partial blank to do exact search, set partial to TRUE for partial search on all entered names
# Returns list of tuples with PatientID, First Name, Middle Name, Last Name
def searchPatientWithName(fname, mname, lname, encryptionKey, fixedSalt, partial=False):
    conn = getConnection()
    cursor = conn.cursor()
    if (not partial):
        if(fname != None):
            if(mname != None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s)
                        FROM Patient
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt
                    )
            elif(mname == None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt
                    )
        elif (mname != None):
            if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt,
                        lname, fixedSalt
                    )
            else:
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt
                    )
        else:
            sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY
                        pgp_sym_decrypt(first_name, %s) ASC;"""
            params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        lname, fixedSalt,
                        encryptionKey
                    )
    else:
        if(fname != None):
            if(mname != None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s)
                        FROM Patient
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt
                    )
            elif(mname == None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt
                    )
        elif (mname != None):
            if(lname != None): 
                        sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                            FROM Patient
                            WHERE middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                            AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                        params = (
                            encryptionKey,
                            encryptionKey,
                            encryptionKey,
                            mname, fixedSalt,
                            lname, fixedSalt
                        )
            else:
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                        FROM Patient
                        WHERE middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt
                    )
        else:
                sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) 
                            FROM Patient
                            WHERE last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')];"""
                params = (
                            encryptionKey,
                            encryptionKey,
                            encryptionKey,
                            lname, fixedSalt
                        )
    
    cursor.execute(sql,params)
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return(patients)       
# searchPatientWithID takes patientID to find the rest of the patient data
# Returns tuple of First Name, Middle Name, Last Name, Mailing Address
# tuple of Family Doctor's Username, First Name, Last Name
# and a list of tuples with admission_id, admission_datetime
def searchPatientWithID(patientID, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s), pgp_sym_decrypt(mailing_address, %s), family_doctor_id  
            FROM patient
            WHERE patient_id = %s"""
    params = (
         encryptionKey,
         encryptionKey,
         encryptionKey,
         encryptionKey,
         patientID
    )
    cursor.execute(sql, params)
    results = cursor.fetchone()
    patientData = results[:-1]
    doctorID = results[-1]

    sql = """SELECT pgp_sym_decrypt(username, %s),  pgp_sym_decrypt(first_name, %s),  pgp_sym_decrypt(last_name, %s)
            FROM staff
            WHERE user_id = %s"""
    params = (
         encryptionKey,
         encryptionKey,
         encryptionKey,
         doctorID
    )
    cursor.execute(sql, params)
    doctorUsername = cursor.fetchone()

    sql = """SELECT admission_id, pgp_sym_decrypt(admittance_datetime, %s)
            FROM admission
            WHERE patient_ID = %s"""
    params = (
         encryptionKey,
         patientID
    )
    cursor.execute(sql, params)
    patientAdmissions = cursor.fetchall()

    return patientData, doctorUsername, patientAdmissions
    

def searchStaffWithUsername():
    print('Under Construction')

def searchStaffWithID():
    print('Under Construction')

def searchBillingWithAdmission(admissionID):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT billing_id, total_amount_owed::FLOAT, total_amount_paid::FLOAT, insurance_paid::FLOAT
        FROM Billing
        WHERE admission_id = %s;"""
    params = (
        admissionID,
    )
    cursor.execute(sql, params)
    results = cursor.fetchone()
    billing = results[1:]
    billingID = str(results[0])
    sql = """SELECT item_description, charge_amount::FLOAT
        FROM billingdetail
        WHERE billing_id = %s;"""
    params = (
        billingID,
    )
    cursor.execute(sql, params)
    billingDetails = cursor.fetchall()
    cursor.close()
    conn.close()
    return billing, billingDetails


if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    #print(passwordMatch('BlairStafford', 'qwertyuiop', keys[1]))
    #print(searchPatientWithName('W', None, None, keys[0], keys[1], True))
    #for patient in searchPatientWithName(None, None, "Stafford", keys[0], keys[1]):
        #print(patient)
    #print(searchBillingWithAdmission('200'))
    print(searchPatientWithID('81', keys[0]))