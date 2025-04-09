import hospitalDB
import EncryptionKey
# searchPatientWithName takes the names as input and searches for the patient in the database
# The function automatically chooses which SQL to execute based on the given parameters
# i.e. missing names
# leave partial blank to do exact search, set partial to TRUE for partial search on all entered names
# Returns list of tuples with PatientID, First Name, Middle Name, Last Name
# USE CASE: search for patients on the search page
def passwordMatch(staffID, password):

    with hospitalDB.get_cursor() as cursor:
        sql = """SELECT (password_hash = crypt(%s, password_hash)) AS password_match
        FROM user_id = %s;"""
        params = (
            password,
            staffID
        )
        cursor.execute(sql, params)
        match = cursor.fetchone()[0]
        cursor.close()
        return(match)

def searchPatientWithName(fixedSalt, fname=None, mname=None, lname=None, partial_fields=set()):
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
        if (usertype == 'Volunteer'):
            base_sql = """SELECT sv.patient_id, sv.first_name, 
                                sv.middle_name, sv.last_name
                        FROM PatientSearchView sv
                        JOIN (SELECT * FROM admission WHERE discharge_datetime IS NULL) AS a ON sv.patient_id = a.patient_id
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
        cursor.close()
    return patients

# searchPatientWithID takes patientID to find the rest of the patient data
# Returns tuple of First Name, Middle Name, Last Name, Mailing Address
# tuple of Family Doctor's Username, First Name, Last Name
# and a list of tuples with admission_id, admission_datetime
# and a list of tuples with emergency contact name, phone number
# USE CASE: Retrieve a patient's information for populating their related page in the GUI
def searchPatientWithID(patientID):
    usertype = hospitalDB.getCurrentUserType()
    print(usertype)
    sql = {'Volunteer': "SELECT * FROM VolunteerView WHERE patient_ID = %s",
           'Office Staff': "SELECT * FROM officestaffview WHERE patient_ID = %s;",
           'Medical Personnel': "SELECT * FROM patientadmissionoverview WHERE patient_ID = %s;",
           'Physician' : "SELECT * FROM patientadmissionoverview WHERE patient_ID = %s;"}
    with hospitalDB.get_cursor() as cursor:
        params = (patientID, )
        cursor.execute(sql[usertype], params)
        patientData = cursor.fetchall()
    return patientData
# searchStaffWithName uses same logic as searchPatientWithName to find and list Staff members
# Returns list of tuples with user_id, first_name, last_name
# USE CASE: search for staff members on the search screen    
def searchStaffWithName(fname, lname, encryptionKey, fixedSalt, partial = False):
    with hospitalDB.get_cursor() as cursor:
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
    return(staff)
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
        cursor.execute(sql, params)
        doctors = cursor.fetchall()
        cursor.close()
    return doctors
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
        cursor.close()

    return staffData
# searchBillingWithAdmission takes the admissionID and returns all billing information and Itemized Bill
# returns tuple with price owed, price paid, price paid by insurance
# returns a list of tuples with billed item, cost
# USE CASE: Find all billing information for printing reports
def searchBillingWithAdmission(admissionID):
    with hospitalDB.get_cursor() as cursor:
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
        cursor.close()
    return admissionData, location, doctor, prescriptions, procedures, notes

def getAvailableLocations():
    with hospitalDB.get_cursor() as cursor:
        cursor.execute("SELECT * FROM availablelocationview;")
        rooms = cursor.fetchall()
    return rooms
if __name__ == "__main__":
    keys = EncryptionKey.getKeys()
    fixedSalt = keys[1]
    #print(passwordMatch('BlairStafford', 'qwertyuiop', keys[1]))
    print(searchPatientWithName(fixedSalt,fname='A', partial_fields={'fname'}, is_volunteer=True))
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