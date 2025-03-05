from hospitalDB import getConnection
import EncryptionKey

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
                        WHERE last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex');"""
            params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        lname, fixedSalt
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
def searchPatientWithID():
    print('Under Construction')

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
         admissionID
    )
    cursor.execute(sql, params)
    results = cursor.fetchone()
    billing = results[1:]
    billingID = results[0]
    sql = """SELECT item_description, charge_amount::FLOAT
        FROM billingdetail
        WHERE billing_id = %s;"""
    params = (
        str(billingID)
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
    for patient in searchPatientWithName(None, "J", None, keys[0], keys[1], True):
        print(patient)
    #print(searchBillingWithAdmission('1'))