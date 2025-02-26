import psycopg2
import hospitalDB
import InsertData
import EncryptionKey
import datetime

keys = EncryptionKey.getKeys()
# hospitalDB creates the database and all user tables
hospitalDB.run()
# Connect to the database
con = psycopg2.connect(
    database="huntsvillehospital",
    user='postgres',
    password='49910',
    host='localhost',
    port= '5432'
  )
con.autocommit = True
cursor = con.cursor()

# Ask User for input data

while True:
    mode = input("Select Mode:\n1. Register User\n2. Register Patient\n3. Process Admission\n")
    if(mode == '1'):
        username = input("Enter Username\n")
        password = input("Enter Password\n")
        firstname = input("Enter Firstname\n")
        lastname = input("Enter lastname\n")
        type = input("Enter Type\n")
        #Insert Data will perform the SQL to add the user to the database and encrypt the password
        InsertData.insertStaff(cursor, firstname , lastname, username, password, type, keys[0], keys[1])
    elif(mode == '2'):
        fName = input("Enter Patient's First Name\n")
        mName = input("Enter Patient's Middle Name\n")
        lName = input("Enter Patient's Last Name\n")
        mAddress = input("Enter Patient's Mailing Address\n")
        hPhone = input("Enter Patient's Home Phone Number\n")
        mPhone = input("Enter Patient's Mobile Phone Number\n")
        wPhone = input("Enter Patient's Work Phone Number\n")
        c1Name = input("Enter Patient's 1st Contact Name\n")
        c1Phone = input("Enter Patient's 1st Contact Phone Number\n")
        c2Name = input("Enter Patient's 2nd Contact Name\n")
        c2Phone = input("Enter Patient's 2nd Contact Phone Number\n")
        fDoctor = input("Enter Patient's Family Doctor\n")
        insCarrier = input("Enter Patient's Insurance Carrier\n")
        insAcc = input("Enter Patient's Insurance Account Number\n")
        insGNum = input("Enter Patient's Insurance Group Number\n")
        con.autocommit = False
        InsertData.insertPatient(cursor, lName, fName, mName, mAddress,  hPhone, mPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, fDoctor,
                  insCarrier, insAcc, insGNum, keys[0], keys[1])
        con.commit()
        con.autocommit = True
    elif(mode == '3'):
        prescriptions = []
        notes = []
        procedures = []
        fName = input("Enter Patient's First Name\n")
        mName = input("Enter Patient's Middle Name\n")
        lName = input("Enter Patient's Last Name\n")
        admissionDateTime = input("Enter Admission Date and Time (YYYY-MM-DD HH:MM:SS)\n")
        admissionReason = input("Enter Patient's Reason for Admission\n")
        releaseDateTime = input("Enter Release Date and Time (YYYY-MM-DD HH:MM:SS)\n")
        hospitalFacility = input("Enter Hospital Facility of Patient's Stay\n")
        hospitalFloor = input("Enter Floor of Patient's Stay\n")
        hospitalRoom = input("Enter Room Number of Patient's Stay\n")
        hospitalBed = input("Enter Bed Number of Patient's Stay\n")
        prescriptionsYesNo = input("Did the Patient have any Prescriptions Administered During Stay? (Y/N)\n")
        if(prescriptionsYesNo.lower() == "y"):
            while(True):
                prescriptionName = input("Enter Name of Prescription\n")
                prescriptionAmount = input("Enter Amount of Prescription Administered\n")
                prescriptionSchedule = input("Enter the Prescription Schedule\n")
                prescription = {'name': prescriptionName, 'amount': prescriptionAmount, 'schedule': prescriptionSchedule}
                prescriptions.append(prescription)
                anotherPrescription = input("Add Another Prescription? (Y/N)\n")
                if(anotherPrescription.lower() == "n"):
                    break
        else:
            print("No Prescriptions Administered\n")
            prescription = {'name': 'None', 'amount': 'None', 'schedule': 'None'}
            prescriptions.append(prescription)
        notesYesNo = input("Are There Any Notes on the Admission? (Y/N)\n")
        if(notesYesNo.lower() == 'y'):
            while(True):
                noteAuthor = input("Enter the Author's Username\n")
                noteType = input("Nurse's of Doctor's Note? (Doctor/Nurse)\n")
                noteText = input("Enter Contents of Note\n")
                timestamp = datetime.datetime.now()
                note = {'author': noteAuthor, 'type': noteType, 'text': noteText, 'time' : timestamp}
                notes.append(note)
                anotherNote = input("Add Another Note? (Y/N)\n")
                if(anotherNote.lower() == "n"):
                    break
        else:
            print("No Notes Entered\n")
            note = {'author': 'None', 'type': 'None', 'text': 'None', 'time' : datetime.datetime.now()}
            notes.append(note)
        proceduresYesNo = input("Does the Patient Require any Procedures? (Y/N)\n")
        if(proceduresYesNo.lower() == 'y'):
            while(True):
                procedureName = input("Enter the Procedure's Name\n")
                procedureDate = input("Enter the Procedure Date (YYYY-MM-DD HH:MM:SS)\n")
                procedure = {'name': procedureName, 'date': procedureDate}
                procedures.append(procedure)
                anotherProcedure = input("Add Another Procedure? (Y/N)\n")
                if(anotherProcedure.lower() == "n"):
                    break
        else:
            print("No Procedures Entered\n")
            procedure = {'name': 'None', 'date': 'None'}
            procedures.append(procedure)
        billingTotal = input("Enter the Total Dollar Amount Owed\n")
        billingPaid = input("Enter the Dollar Amount Paid\n")
        billingInsurance = input("Enter the Dollar Amount Paid by Insurance\n")
        itemizedBill = []
        while(True):
            billItem = input("Enter The Billed Item\n")
            itemCost = input("Enter The Item's Price\n")
            item = {'name': billItem, 'cost': float(itemCost)}
            itemizedBill.append(item)
            anotherItem = input("Add Another Item (Y/N)\n")
            if(anotherItem.lower() == "n"):
                    break
        con.autocommit = False
        InsertData.insertAdmission(cursor, fName, mName, lName, admissionDateTime, admissionReason, releaseDateTime, hospitalFacility, hospitalFloor, hospitalRoom, hospitalBed, prescriptions, notes, procedures, billingTotal, billingPaid, billingInsurance, itemizedBill, keys[0], keys[1])
        con.commit()
        con.autocommit = True
    quit = input("Would you like to make another addition? (Y/N)\n")
    if quit.lower() == "n":
        break