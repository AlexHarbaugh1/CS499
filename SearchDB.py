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
# USE CASE: search for patients on the search page
def searchPatientWithName(fname, mname, lname, encryptionKey, fixedSalt, partial=False):
    conn = getConnection()
    cursor = conn.cursor()
    if (not partial):
        if(fname != None):
            if(mname != None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM SearchView
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
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt
                    )
            elif(mname == None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt
                    )
        elif (mname != None):
            if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt,
                        lname, fixedSalt
                    )
            else:
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE middle_name_prefix_trgms[array_upper(middle_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt
                    )
        else:
            sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
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
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        mname, fixedSalt
                    )
            elif(mname == None):
                if(lname != None): 
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt,
                        lname, fixedSalt
                    )
                else:
                     sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                     params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        fname, fixedSalt
                    )
        elif (mname != None):
            if(lname != None): 
                        sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                            FROM searchview
                            WHERE middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                            AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                        params = (
                            encryptionKey,
                            encryptionKey,
                            encryptionKey,
                            mname, fixedSalt,
                            lname, fixedSalt
                        )
            else:
                    sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                        FROM searchview
                        WHERE middle_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
                    params = (
                        encryptionKey,
                        encryptionKey,
                        encryptionKey,
                        mname, fixedSalt
                    )
        else:
                sql = """SELECT patient_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                            FROM searchview
                            WHERE last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                        ORDER BY decrypted_last_name ASC;"""
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
# and a list of tuples with emergency contact name, phone number
# USE CASE: Retrieve a patient's information for populating their related page in the GUI
def searchPatientWithID(patientID, usertype):
    sql = {'volunteer_role': "SELECT * FROM VolunteerView WHERE patient_ID = %s",
           'officestaff_role': "SELECT * FROM officestaffview WHERE patient_ID = %s;",
           'medicalpersonel_role': "SELECT * FROM medicalpersonelview WHERE patient_ID = %s;",
           'physician_role' : "SELECT * FROM physicianview WHERE patient_ID = %s;"}
    conn = getConnection()
    cursor = conn.cursor()
    params = (patientID, )
    cursor.execute(sql[usertype], params)
    patientData = cursor.fetchall()
    return patientData
# searchStaffWithName uses same logic as searchPatientWithName to find and list Staff members
# Returns list of tuples with user_id, first_name, last_name
# USE CASE: search for staff members on the search screen    
def searchStaffWithName(fname, lname, encryptionKey, fixedSalt, partial = False):
    conn = getConnection()
    cursor = conn.cursor()
    if (not partial):
        if(fname != None):
            if(lname != None): 
                sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                    WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                    AND last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                    ORDER BY decrypted_last_name ASC;"""
                params = (
                    encryptionKey,
                    encryptionKey,
                    fname, fixedSalt,
                    lname, fixedSalt
                )
            else:
                sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                    WHERE first_name_prefix_trgms[array_upper(first_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                    ORDER BY decrypted_last_name ASC;"""
                params = (
                    encryptionKey,
                    encryptionKey,
                    fname, fixedSalt
                    )
        else:
            sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                        WHERE last_name_prefix_trgms[array_upper(last_name_prefix_trgms, 1)] = encode(digest(%s || %s, 'sha256'), 'hex')
                        ORDER BY decrypted_last_name ASC;"""
            params = (
                        encryptionKey,
                        encryptionKey,
                        lname, fixedSalt,
                    )
    else:
        if(fname != None):
            if(lname != None): 
                sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                    WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                    AND last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                    ORDER BY decrypted_last_name ASC;"""
                params = (
                    encryptionKey,
                    encryptionKey,
                    fname, fixedSalt,
                    lname, fixedSalt
                )
            else:
                    sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                    WHERE first_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                    ORDER BY decrypted_last_name ASC;"""
                    params = (
                    encryptionKey,
                    encryptionKey,
                    fname, fixedSalt
                )
        else:
                sql = """SELECT user_id, pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s) AS decrypted_last_name
                    FROM staff
                    WHERE last_name_prefix_trgms && ARRAY[encode(digest(%s || %s, 'sha256'), 'hex')]
                    ORDER BY decrypted_last_name ASC;"""
                params = (
                            encryptionKey,
                            encryptionKey,
                            lname, fixedSalt
                        )
    
    cursor.execute(sql,params)
    staff = cursor.fetchall()
    cursor.close()
    conn.close()
    return(staff)
# searchStaffWithID takes input user_id and returns relevant staff member information
# Returns tuple of username, first_name, last_name, type
# USE CASE: after selecting a staff member, return the data necessary to populate the page
def searchStaffWithID(userID, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT pgp_sym_decrypt(username, %s), pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s), type_name
            FROM staff NATURAL JOIN usertype
            WHERE user_id = %s"""
    params = (
         encryptionKey,
         encryptionKey,
         encryptionKey,
         userID
    )
    cursor.execute(sql, params)
    staffData = cursor.fetchone()

    return staffData
# searchBillingWithAdmission takes the admissionID and returns all billing information and Itemized Bill
# returns tuple with price owed, price paid, price paid by insurance
# returns a list of tuples with billed item, cost
# USE CASE: Find all billing information for printing reports
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
# searchAdmissionWithID takes the admission ID and returns all associated admissionData
# Returns tuple with tuple of admittance date, release date, reason for admission
# tuple of facility, floor, room number, bed number
# tuple of doctor first name, last name
# list of tuples with prescription name, amount, schedule
# list of tuples with procedure name, scheduled time
# list of tuples with note author's first name, last name, type of note, note text, note time written
# USE CASE: retrieve all necessary data for populating the GUI and printing reports
def searchAdmissionWithID(admissionID, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT pgp_sym_decrypt(admittance_datetime, %s), pgp_sym_decrypt(discharge_datetime, %s), pgp_sym_decrypt(reason_for_admission, %s), doctor_id, location_id
            FROM admission
            WHERE admission_id = %s;"""
    params = (
        encryptionKey,
        encryptionKey,
        encryptionKey,
        admissionID
    )
    cursor.execute(sql, params)
    results = cursor.fetchone()
    locationID = results[-1]
    doctorID = results[-2]
    admissionData = results[:-2]
    sql = """SELECT facility, floor, room_number, bed_number
            FROM location
            WHERE location_id = %s"""
    params = (
         locationID,
         )
    cursor.execute(sql, params)
    location = cursor.fetchone()
    sql = """SELECT pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s)
            FROM staff 
            WHERE user_id = %s;"""
    params = (
         encryptionKey,
         encryptionKey,
         doctorID
    )
    cursor.execute(sql, params)
    doctor = cursor.fetchone()
    sql = """SELECT pgp_sym_decrypt(medication_name, %s), pgp_sym_decrypt(amount, %s), pgp_sym_decrypt(schedule, %s)
            FROM prescription
            WHERE admission_id = %s"""
    params = (
        encryptionKey,
        encryptionKey,
        encryptionKey,
        admissionID
    )
    cursor.execute(sql, params)
    prescriptions = cursor.fetchall()
    sql = """SELECT pgp_sym_decrypt(procedure_name, %s), pgp_sym_decrypt(scheduled_datetime, %s)
    FROM scheduledprocedure
    WHERE admission_id = %s"""
    params = (
        encryptionKey,
        encryptionKey,
        admissionID
    )
    cursor.execute(sql, params)
    procedures = cursor.fetchall()
    sql = """SELECT pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s), note_type, pgp_sym_decrypt(note_text, %s), pgp_sym_decrypt(note_datetime, %s)
            FROM patientnote n JOIN staff s ON n.author_id = s.user_id
            WHERE admission_id = %s"""
    params = (
        encryptionKey,
        encryptionKey,
        encryptionKey,
        encryptionKey,
        admissionID
    )
    cursor.execute(sql, params)
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return admissionData, location, doctor, prescriptions, procedures, notes
     
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    #print(passwordMatch('BlairStafford', 'qwertyuiop', keys[1]))
    #print(searchPatientWithName(None, None, 'J', keys[0], keys[1], True))
    #for patient in searchPatientWithName("Ashley", None, None, keys[0], keys[1]):
        #print(patient)
    #print(searchBillingWithAdmission('200'))
    print(searchPatientWithID('2', 'volunteer_role'))
    #print(searchStaffWithName('S', None, keys[0], keys[1], True))
    #print(searchStaffWithID('51', keys[0]))
    """admissionData, location, assignedDoctor, prescriptions, procedures, notes = searchAdmissionWithID('10', keys[0])
    print(admissionData)
    print(location)
    print(assignedDoctor)
    print(prescriptions)
    print(procedures)
    print(notes)"""