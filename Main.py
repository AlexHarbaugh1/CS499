import hospitalDB
import SearchDB
import EncryptionKey
hospitalDB.run()
import InsertData
import datetime
keys = EncryptionKey.getKeys()
while True:
    username = input("username: ")
    password = input("password: ")
    if (hospitalDB.userLogin(username, password, keys[1])):
        print(hospitalDB.getCurrentUserType())
        while(True):
            mode = input("""Select Application:
                        1. Search Patient By Name
                        2. Search Admissions By Date
                        3. Register Patient
                        4. Register Admission
                        5. Register Staff Member
                        6. Register Location
                        """)
            if mode == '1':
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
                        while True:
                            admissionmode = input("""Select Function:
                                            1. Insert Note
                                            2. Insert Procedure
                                            3. Insert Procedure
                                            """)
                            if admissionmode == '1':
                                noteText = input("Input Note Text: ")
                                InsertData.insertNote(results[0][0], admissionID, noteText)
                            elif admissionmode == '2':
                                procedureName = input("Enter Procedure Name: ")
                                procedureSchedule = input("Enter Procedure Date and Time: ")
                                InsertData.insertProcedure(results[0][0], admissionID, procedureName, procedureSchedule)
                            elif admissionmode == '3':
                                prescriptionName = input("Enter Prescription Name: ")
                                prescriptionAmount = input("Enter Prescription Amount: ")
                                prescriptionSchedule = input("Enter Prescription Schedule: ")
                                InsertData.insertPrescription(results[0][0], admissionID, prescriptionName, prescriptionAmount, prescriptionSchedule)
                            else: break

            elif mode == '2':
                print('To Be Added')
            elif mode == '3':
                patientfname = input("First Name: ")
                patientmname = input("Middle Name: ")
                patientlname = input("Last Name: ")
                patientAddress = input("Address: ")
                for doctor in SearchDB.getDoctors(keys[0]):
                    print(doctor)
                patientDoctor = input("Family Doctor ID: ")
                InsertData.insertPatient(patientfname, patientmname, patientlname, patientAddress, patientDoctor, keys[1])
            elif mode == '4':
                searchName = input("Enter Last Name: ")
                results = SearchDB.searchPatientWithName(keys[1], fname=None, mname=None, lname=searchName, partial_fields={'lname'})
                for patient in results:
                    print(patient)
                patientID = input("Enter PatientID to Select: ")
                results = SearchDB.getAvailableLocations()
                for item in results:
                    print(item)
                locationID = input("Select Location ID from Available Locations: ")
                admissionReason = input("Insert Breif Reason for Admission: ")
                InsertData.insertAdmission(patientID, locationID, datetime.datetime.now(), admissionReason)
            elif mode == '5':
                print('To be added')
            elif mode == '6':
                facility = input("Facility Name: ")
                floor = input("Floor: ")
                room = input("Room: ")
                bed = input("Bed: ")
                InsertData.insertLocation(facility, floor, room, bed)
            else: break