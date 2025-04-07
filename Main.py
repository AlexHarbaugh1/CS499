import hospitalDB
import SearchDB
import EncryptionKey
hospitalDB.run()
import InsertData
keys = EncryptionKey.getKeys()
username = input("username: ")
password = input("password: ")
if (hospitalDB.userLogin(username, password, keys[1])):
    while(True):
        mode = input("""Select Application:
                     1. Register Patient
                     2. Search Patient
                     3. Register Admission
                     """)
        if mode == '1':
            patientfname = input("First Name: ")
            patientmname = input("Middle Name: ")
            patientlname = input("Last Name: ")
            patientAddress = input("Address: ")
            for doctor in SearchDB.getDoctors(keys[0]):
                print(doctor)
            patientDoctor = input("Family Doctor ID: ")
            InsertData.insertPatient(patientfname, patientmname, patientlname, patientAddress, patientDoctor, keys[1])
        elif mode == '2':
            searchName = input("Enter Last Name: ")
            results = SearchDB.searchPatientWithName(keys[1], fname=None, mname=None, lname=searchName, partial_fields={'lname'})
            for patient in results:
                print(patient)
            id = input("Enter Patient ID to View Data: ")
            results = SearchDB.searchPatientWithID(id)
            for item in results:
                print(item)
            while(True):
                patientmode = input("""Select Function:
                                    1. View Admission
                                    2. Edit Information
                                    """)
                if patientmode == '1':
                    admissionID = input("Enter Admission ID to view: ")
                    print(SearchDB.searchAdmissionWithID(admissionID, keys[0]))
        admissionID = input("Enter Admission ID to enter Note: ")
        noteText = input("Input Note Text: ")
        InsertData.insertNote(results[0][0], admissionID, noteText)
        results = SearchDB.searchPatientWithID(id)
        procedureName = input("Enter Procedure Name: ")
        procedureSchedule = input("Enter Procedure Date and Time: ")
        InsertData.insertProcedure(results[0][0], admissionID, procedureName, procedureSchedule)
        prescriptionName = input("Enter Prescription Name: ")
        prescriptionAmount = input("Enter Prescription Amount: ")
        prescriptionSchedule = input("Enter Prescription Schedule: ")
        InsertData.insertPrescription(results[0][0], admissionID, prescriptionName, prescriptionAmount, prescriptionSchedule)

