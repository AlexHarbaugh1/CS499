import hospitalDB
import SearchDB
import EncryptionKey
hospitalDB.run()
keys = EncryptionKey.getKeys()
username = input("username: ")
password = input("password: ")
if (hospitalDB.userLogin(username, password, keys[1])):
    searchName = input("Enter Last Name: ")
    results = SearchDB.searchPatientWithName(keys[1], fname=None, mname=None, lname=searchName, partial_fields={'lname'})
    for patient in results:
        print(patient)
    id = input("Enter Patient ID to View Data: ")
    results = SearchDB.searchPatientWithID(id)
    for item in results:
        print(item) 