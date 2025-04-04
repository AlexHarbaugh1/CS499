import hospitalDB
import SearchDB
import EncryptionKey
hospitalDB.run()
keys = EncryptionKey.getKeys()
username = input("username: ")
password = input("password: ")
if (hospitalDB.userLogin(username, password, keys[1])):
    conn = hospitalDB.getConnection()
    cursor = conn.cursor()
    conn.commit()
    searchName = input("Enter Last Name: ")
    results = SearchDB.searchPatientWithName(None, None, searchName, keys[0], keys[1], True)
    for patient in results:
        print(patient)
    id = input("Enter Patient ID to View Data: ")
    results = SearchDB.searchPatientWithID(id, keys[0])
    for item in results:
        print(item)