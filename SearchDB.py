import hospitalDB
import psycopg2
import EncryptionKey
import datetime
# passwordMatch checks if the entered password is the same as the saved password
# Return TRUE or FALSE
def passwordMatch(username, password, fixedSalt):
    conn = getConnection()
    cursor = conn.cursor()
    sql = """SELECT (password_hash = crypt(%s, password_hash)) AS password_match
             FROM Staff WHERE username_hash = encode(digest(%s || %s, 'sha256'), 'hex');"""
    
    params = (password, username, fixedSalt)
    cursor.execute(sql, params)
    
    result = cursor.fetchone()
    match = result[0] if result is not None else False  # <- Safely handles no result
    
    cursor.close()
    conn.close()
    return match

# searchPatientWithName takes the names as input and searches for the patient in the database
# The function automatically chooses which SQL to execute based on the given parameters
# i.e. missing names
# leave partial blank to do exact search, set partial to TRUE for partial search on all entered names
# Returns list of tuples with PatientID, First Name, Middle Name, Last Name
# USE CASE: search for patients on the search page
def passwordMatch(staffID, password):

    with hospitalDB.get_cursor() as cursor:
        current_role = hospitalDB.getCurrentUserType()
        cursor.execute("SET ROLE postgres;")
        sql = """SELECT (password_hash = crypt(%s, password_hash)) AS password_match
        FROM staff WHERE user_id = %s;"""
        params = (
            password,
            staffID
        )
        cursor.execute(sql, params)
        match = cursor.fetchone()[0]
        role = current_role.lower().replace(" ", "") + "_role"
        sql = """SET ROLE %s;"""
        params = (role,)
        cursor.execute(sql, params)
        return(match)

def searchPatientWithName(fixedSalt, fname=None, mname=None, lname=None, partial_fields=set(), active_admissions_only=False):
    with hospitalDB.get_cursor() as cursor:
        usertype = hospitalDB.getCurrentUserType()
        conditions = []
        params = []
        name_parts = [
            (fname, 'first_name_prefix_trgms', 'fname'),
            (mname, 'middle_name_prefix_trgms', 'mname'),
            (lname, 'last_name_prefix_trgms', 'lname'),
        ]

        for value, column, field in name_parts:
            if value:
                hashed = "encode(digest(%s || %s, 'sha256'), 'hex')"
                
                # Choose operator based on whether field is in partial_fields
                if field in partial_fields:
                    condition = f"{column} && ARRAY[{hashed}]"  # Partial match
                else:
                    condition = f"{column}[array_upper({column}, 1)] = {hashed}"  # Exact match
                    
                conditions.append(condition)
                params.extend([value, fixedSalt])

        # Base query construction
        if usertype == 'Volunteer':
            base_sql = """SELECT sv.patient_id, sv.first_name, 
                                sv.middle_name, sv.last_name
                        FROM PatientSearchView sv
                        JOIN (SELECT * FROM admission WHERE discharge_datetime IS NULL) AS a ON sv.patient_id = a.patient_id
                        JOIN approvedvisitors v on a.admission_id = v.admission_id
                        """
        else:
            if active_admissions_only:
                base_sql = """SELECT sv.patient_id, sv.first_name, 
                                sv.middle_name, sv.last_name
                        FROM PatientSearchView sv
                        JOIN (SELECT patient_id FROM admission WHERE discharge_datetime IS NULL) AS a ON sv.patient_id = a.patient_id
                        """
            else:
                base_sql = "SELECT patient_id, first_name, middle_name, last_name FROM PatientSearchView"

        # Add conditions if any exist
        if conditions:
            sql = f"{base_sql} WHERE {' AND '.join(conditions)}"
        else:
            sql = base_sql

        sql += " ORDER BY last_name ASC;"
        cursor.execute(sql, params)
        patients = cursor.fetchall()
        
    return patients

# searchPatientWithID takes patientID to find the rest of the patient data
# Returns tuple of First Name, Middle Name, Last Name, Mailing Address
# tuple of Family Doctor's Username, First Name, Last Name
# and a list of tuples with admission_id, admission_datetime
# and a list of tuples with emergency contact name, phone number
# USE CASE: Retrieve a patient's information for populating their related page in the GUI
def searchPatientWithID(patientID):
    usertype = hospitalDB.getCurrentUserType()
    sql = {'Volunteer': "SELECT * FROM VolunteerView WHERE patient_id = %s",
           'Office Staff': "SELECT * FROM officestaffview WHERE patient_id = %s;",
           'Medical Personnel': "SELECT * FROM patientadmissionoverview WHERE patient_id = %s;",
           'Physician' : "SELECT * FROM patientadmissionoverview WHERE patient_id = %s;",
           'Administrator' : "SELECT * FROM patientadmissionoverview WHERE patient_id = %s;"}
    with hospitalDB.get_cursor() as cursor:
        params = (patientID, )
        cursor.execute(sql[usertype], params)
        patientData = cursor.fetchone()
    return patientData
def searchPatientWithID(patientID, encryptionKey):
    conn = getConnection()
    cursor = conn.cursor()

    sql = """
    SELECT pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(middle_name, %s), pgp_sym_decrypt(last_name, %s), pgp_sym_decrypt(mailing_address, %s), family_doctor_id
    FROM patient
    WHERE patient_id = %s
    """
    params = (encryptionKey, encryptionKey, encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    results = cursor.fetchone()
    if not results:
        return None
    patientData = results[:-1]
    doctorID = results[-1]

    sql = """
    SELECT pgp_sym_decrypt(username, %s), pgp_sym_decrypt(first_name, %s), pgp_sym_decrypt(last_name, %s)
    FROM staff
    WHERE user_id = %s
    """
    params = (encryptionKey, encryptionKey, encryptionKey, doctorID)
    cursor.execute(sql, params)
    doctorUsername = cursor.fetchone() or ("Unknown", "Unknown", "Unknown")

    sql = """
    SELECT admission_id, pgp_sym_decrypt(admittance_datetime, %s), pgp_sym_decrypt(reason_for_admission, %s), pgp_sym_decrypt(discharge_datetime, %s)
    FROM admission
    WHERE patient_ID = %s
    """
    params = (encryptionKey, encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    patientAdmissions = cursor.fetchall()

    sql = """
    SELECT pgp_sym_decrypt(carrier_name, %s), pgp_sym_decrypt(account_number, %s), pgp_sym_decrypt(group_number, %s)
    FROM insurance
    WHERE patient_id = %s
    """
    params = (encryptionKey, encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    patientInsurance = cursor.fetchone()

    sql = """
    SELECT phone_type, pgp_sym_decrypt(phone_number, %s)
    FROM phonenumber
    WHERE patient_id = %s
    """
    params = (encryptionKey, patientID)
    cursor.execute(sql, params)
    phoneNumbers = cursor.fetchall()

    sql = """
    SELECT pgp_sym_decrypt(contact_name, %s), pgp_sym_decrypt(contact_phone, %s)
    FROM emergencycontact
    WHERE patient_id = %s
    ORDER BY contact_order
    """
    params = (encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    emergencyContacts = cursor.fetchall()

    sql = """
    SELECT facility, floor, room_number, bed_number
    FROM location
    WHERE location_id = (
        SELECT location_id FROM admission WHERE patient_id = %s LIMIT 1
    )
    """
    params = (patientID,)
    cursor.execute(sql, params)
    locationInfo = cursor.fetchone()

    sql = """
    SELECT pgp_sym_decrypt(note_text, %s), pgp_sym_decrypt(note_datetime, %s)
    FROM patientnote
    WHERE LOWER(note_type) = 'doctor'
    AND admission_id IN (
        SELECT admission_id FROM admission WHERE patient_id = %s
    )
    ORDER BY note_datetime
    """
    params = (encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    doctorNotes = cursor.fetchall()

    sql = """
    SELECT pgp_sym_decrypt(note_text, %s), pgp_sym_decrypt(note_datetime, %s)
    FROM patientnote
    WHERE LOWER(note_type) = 'nurse'
    AND admission_id IN (
        SELECT admission_id FROM admission WHERE patient_id = %s
    )
    ORDER BY note_datetime
    """
    params = (encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    nurseNotes = cursor.fetchall()

    sql = """
    SELECT pgp_sym_decrypt(medication_name, %s), pgp_sym_decrypt(amount, %s), pgp_sym_decrypt(schedule, %s)
    FROM prescription
    WHERE admission_id IN (
        SELECT admission_id FROM admission WHERE patient_id = %s
    )
    ORDER BY prescription_id
    """
    params = (encryptionKey, encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    prescriptions = cursor.fetchall()

    sql = """
    SELECT pgp_sym_decrypt(procedure_name, %s), pgp_sym_decrypt(scheduled_datetime, %s)
    FROM scheduledprocedure
    WHERE admission_id IN (
        SELECT admission_id FROM admission WHERE patient_id = %s
    )
    ORDER BY scheduled_datetime
    """
    params = (encryptionKey, encryptionKey, patientID)
    cursor.execute(sql, params)
    procedures = cursor.fetchall()

    return patientData, doctorUsername, patientAdmissions, patientInsurance, phoneNumbers, emergencyContacts, locationInfo, doctorNotes, nurseNotes, prescriptions, procedures

# searchStaffWithName uses same logic as searchPatientWithName to find and list Staff members
# Returns list of tuples with user_id, first_name, last_name
# USE CASE: search for staff members on the search screen    
def searchStaffWithName(fixed_salt, fname=None, lname=None, partial_fields=set()):
    with hospitalDB.get_cursor() as cursor:
        conditions = []
        params = []
        name_parts = [
            (fname, 'first_name_prefix_trgms', 'fname'),
            (lname, 'last_name_prefix_trgms', 'lname'),
        ]

        for value, column, field in name_parts:
            if value:
                hashed = "encode(digest(%s || %s, 'sha256'), 'hex')"
                
                # Choose operator based on whether field is in partial_fields
                if field in partial_fields:
                    condition = f"{column} && ARRAY[{hashed}]"  # Partial match
                else:
                    condition = f"{column}[array_upper({column}, 1)] = {hashed}"  # Exact match
                    
                conditions.append(condition)
                params.extend([value, fixed_salt])

        # Base query
        base_sql = """SELECT user_id, username, first_name, last_name, type_name 
                      FROM staffsearchview"""

        # Add conditions if any exist
        if conditions:
            sql = f"{base_sql} WHERE {' AND '.join(conditions)}"
        else:
            sql = base_sql

        sql += " ORDER BY last_name ASC;"
        cursor.execute(sql, params)
        staff = cursor.fetchall()
        
    return staff
# searchStaffWithID takes input user_id and returns relevant staff member information
# Returns tuple of username, first_name, last_name, type
# USE CASE: after selecting a staff member, return the data necessary to populate the page
def getDoctors(encryptionKey):
    with hospitalDB.get_cursor() as cursor:
        sql = """SELECT user_id, username, first_name, last_name
                FROM staffsearchview
                WHERE type_name = 'Physician';"""
        params = (
            encryptionKey,
        )*3
        try:
            cursor.execute(sql, params)
            doctors = cursor.fetchall()
            
            return doctors
        except psycopg2.ProgrammingError as e:
            print("Error: Insufficient privileges to execute this operation")
            return "Error"


def searchStaffWithID(userID, encryptionKey):
    with hospitalDB.get_cursor() as cursor:
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
    with hospitalDB.get_cursor() as cursor:
        sql = """SELECT *
            FROM BillingInformationView
            WHERE admission_id = %s;"""
        params = (
            admissionID,
        )
        cursor.execute(sql, params)
        billDetails = cursor.fetchone()

    return billDetails
# searchAdmissionWithID takes the admission ID and returns all associated admissionData
# Returns tuple with tuple of admittance date, release date, reason for admission
# tuple of facility, floor, room number, bed number
# tuple of doctor first name, last name
# list of tuples with prescription name, amount, schedule
# list of tuples with procedure name, scheduled time
# list of tuples with note author's first name, last name, type of note, note text, note time written
# USE CASE: retrieve all necessary data for populating the GUI and printing reports
def searchAdmissionWithID(admissionID, encryptionKey):
    with hospitalDB.get_cursor() as cursor:
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
        
    return admissionData, location, doctor, prescriptions, procedures, notes

def getLogs(from_date=None, to_date=None, limit=1000):
    with hospitalDB.get_cursor() as cursor:
        conditions = []
        params = []
        
        # Build WHERE clause based on filters
        if from_date:
            conditions.append("timestamp >= %s")
            params.append(from_date)
        
        if to_date:
            # Add one day to include logs from the end date
            to_date_end = to_date + datetime.timedelta(days=1)
            conditions.append("timestamp < %s")
            params.append(to_date_end)
        
        # Base query
        sql = """SELECT * FROM audit_log"""
        
        # Add WHERE clause if we have conditions
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        # Add ORDER BY and LIMIT
        sql += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        logs = cursor.fetchall()
        cursor.close()
        
        return logs
    
def getAvailableLocations():
    with hospitalDB.get_cursor() as cursor:
        cursor.execute("SELECT * FROM availablelocationview;")
        rooms = cursor.fetchall()
    return rooms
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    fixedSalt = keys[1]
    hospitalDB.userLogin('Volunteer1', 'qwertyuiop', fixedSalt)
    print(searchPatientWithID('2'))
    #print(passwordMatch('BlairStafford', 'qwertyuiop', keys[1]))
    #print(searchPatientWithName(fixedSalt,fname='A', partial_fields={'fname'}, is_volunteer=True))
    #searchPatientWithName(fixedSalt, fname=None, mname=None, lname=None, partial_fields={'fname','mname','lname'}, is_volunteer=False) THIS IS THE FORMAT FOR SEARCHING BY NAME PUT FIELDS THAT YOU WANT TO BE PARTIAL SEARCHED INTO THE PARTIAL FIELDS SET
    #for patient in searchPatientWithName("Ashley", None, None, keys[0], keys[1]):
        #print(patient)
    #print(searchBillingWithAdmission('200'))
    #print(searchPatientWithID('2', 'volunteer_role'))
    #print(searchStaffWithName('Blair', None, keys[0], keys[1], True))
    #print(searchStaffWithID('51', keys[0]))
    """admissionData, location, assignedDoctor, prescriptions, procedures, notes = searchAdmissionWithID('10', keys[0])
    print(admissionData)
    print(location)
    print(assignedDoctor)
    print(prescriptions)
    print(procedures)
    print(notes)"""
    #print(searchPatientWithID('71', keys[0]))
    #print(searchStaffWithName('S', None, keys[0], keys[1], True))
    #print(searchStaffWithID('2', keys[0]))

    print(searchAdmissionWithID('2', keys[0]))

    print(searchAdmissionWithID('2', keys[0]))

