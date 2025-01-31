import psycopg2
def insertUser(cursor, username, password, fname, lname, type):
    cursor.execute("""INSERT INTO Users (username, password, firstname, lastname, type)
                   VALUES ('{}', crypt('{}', gen_salt('bf')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), '{}') ;""" .format(username, password, fname, lname, type))

def insertPatient(cursor, lName, fName, mName, address, hPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum, billInfo, amountPaid, amountOwed, insAmountOwed):
    cursor.execute("""INSERT INTO Patients (lastname, firstname, middlename, mailing_address, home_phone, work_phone, contact1_name,
                   contact1_phone, contact2_name, contact2_phone, family_doctor, insurance_carrier, insurance_account,
                   insurance_group_number, billing_information, amount_paid, amount_owed, amount_paid_insurance)
                   VALUES (crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')),
                   crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')),
                   crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}',
                   gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')),
                   crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')), crypt('{}', gen_salt('md5')),
                   crypt('{}', gen_salt('md5'))) ;""" .format( lName, fName, mName, address, hPhone, wPhone, c1Name, c1Phone, c2Name, c2Phone, doctor,
                  insCarrier, insAcc, insGNum, billInfo, amountPaid, amountOwed, insAmountOwed))
def insertPrescription():
    print("hi")
def insertAdmission():
    print("Hi")