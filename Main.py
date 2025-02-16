import psycopg2
import hospitalDB
import InsertData
import EncryptionKey

keys = EncryptionKey.getKeys()
# hospitalDB creates the database and all user tables
hospitalDB.run(keys[0])
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
        lName = input("Enter Patient's Last Name\n")
        mName = input("Enter Patient's Middle Name\n")
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
        print("To be Added")
        #cursor.execute("SELECT crypt('enterpword', '{}') ;" .format(passw))
        #Insert Data will perform the SQL to add the user to the database and encrypt the password
        #InsertData.insertAdmission(cursor, username, password, firstname, lastname, type)1
    quit = input("Would you like to make another addition? (Y/N)\n")
    if quit.lower() == "n":
        break