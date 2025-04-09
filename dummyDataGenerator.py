import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import random
from decimal import Decimal
import hospitalDB
import EncryptionKey
import InsertData
import UpdateDB
# Initialize Faker and DB connection
hospitalDB.run()
fake = Faker()


# Configure for realistic medical data
Faker.seed(42)
random.seed(42)

# --- Helper Functions ---
def generate_phone():
    return f"{fake.random_int(100, 999)}-{fake.random_int(100, 999)}-{fake.random_int(1000, 9999)}"

def generate_prescription():
    meds = ["Aspirin", "Metformin", "Lisinopril", "Amoxicillin", "Omeprazole"]
    return {
        "name": random.choice(meds),
        "amount": f"{random.randint(1, 500)}mg",
        "schedule": random.choice(["Daily", "BID", "TID", "QID"])
    }

def generate_procedure():
    procedures = ["X-Ray", "MRI", "Blood Test", "Echocardiogram", "Colonoscopy"]
    return {
        "name": random.choice(procedures),
        "date": str(fake.date_between(start_date="+1d", end_date="+30d"))
    }

# --- Populate Tables ---

def populate_users( encryptionKey, fixedSalt, n=50):
    types = ['Administrator', 'Medical Personnel', 'Volunteer', 'Office Staff', 'Physician']

    for _ in range(n):
        user_type = random.choice(types)
        username = fake.unique.user_name()
        password = fake.password()
        InsertData.insertStaff(fake.first_name(), fake.last_name(), username, password, user_type, encryptionKey, fixedSalt)

def populate_patients(encryptionKey, fixedSalt, n=100):
    sql = """SELECT pgp_sym_decrypt(username, %s) FROM Staff WHERE type_id = 5"""
    params = (encryptionKey,)
    with hospitalDB.get_cursor() as cursor:
        cursor.execute(sql, params)
        doctor_ids = [row[0] for row in cursor.fetchall()]
    insurances = ['Progressive', 'United Healthcare', 'Allstate', 'Local Provider']
    
    for _ in range(n):
        InsertData.insertPatients(fake.first_name(), fake.first_name() if random.random() < 0.3 else None, fake.last_name(), fake.address(), generate_phone(), generate_phone(), generate_phone(), fake.first_name() + ' ' + fake.last_name(), generate_phone(), fake.first_name() + ' ' + fake.last_name(), generate_phone(), random.choice(doctor_ids), random.choice(insurances), str(fake.random_int(10000, 99999)), str(fake.random_int(10000, 99999)), keys[0], keys[1])


def populate_admissions(encryptionKey, fixedSalt, n=200):
    with hospitalDB.get_cursor() as cursor:
        cursor.execute("SELECT patient_id FROM Patient")
        patient_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT user_id FROM Staff WHERE type_id = 5")
        doctor_ids = [row[0] for row in cursor.fetchall()]
    for _ in range(n):
        admit_date = fake.date_between(start_date="-2y", end_date="today")
        id = random.choice(patient_ids)
        discharge_date = None
        facilities = ["Main Hospital", "North Clinic", "South Clinic"]
        admissionID = InsertData.insertAdmissions(id, str(admit_date), fake.sentence(nb_words=6), discharge_date, random.choice(facilities), random.randint(1, 10), fake.random_int(100, 999), fake.random_int(1, 50), random.choice(doctor_ids), keys[0])
        # Add Approved Visitors (0 - 5, Any)
        visitors = []
        for _ in range(random.randint(1, 5)):
            visitors.append(fake.first_name() + ' ' + fake.last_name())
        InsertData.insertVisitors(admissionID, visitors, encryptionKey)
        # Add prescriptions (1-3 per admission)
        prescriptions = []
        for _ in range(random.randint(1, 3)):
            rx = generate_prescription()
            prescriptions.append(rx)
        InsertData.insertPrescriptions(admissionID, prescriptions, encryptionKey)

        # Add notes (2-5 per admission)
        sql = "SELECT pgp_sym_decrypt(username, %s) FROM Staff WHERE type_id IN (2, 5)"
        params = (encryptionKey,)
        with hospitalDB.get_cursor() as cursor:
            cursor.execute(sql, params)
            staff_ids = [row[0] for row in cursor.fetchall()]
        notes = []
        for _ in range(random.randint(2, 5)):
            note = {'author': random.choice(staff_ids), 'type': random.choice(["Doctor", "Nurse"]), 'text': fake.paragraph(nb_sentences=3), 'time' : fake.date_time_between(start_date=admit_date, end_date=discharge_date or datetime.now())}
            notes.append(note)
        InsertData.insertNotes(admissionID, notes, encryptionKey, fixedSalt)

        # Add procedures (0-2 per admission)
        procedures = []
        for _ in range(random.randint(0, 2)):
            proc = generate_procedure()
            procedures.append(proc)
        if len(procedures) > 0:
            InsertData.insertProcedures(admissionID, procedures, encryptionKey)
        # Add billing
        total_owed = Decimal(random.randint(1000, 100000))
        total_paid = total_owed * Decimal(random.uniform(0.1, 0.9))
        insurance_paid = total_owed - total_paid
        items = ["Room Charge", "Lab Fee", "Medication", "Surgery Fee", "Consultation"]
        # Add billing details (3-10 items)
        itemlist = []
        for _ in range(random.randint(3, 10)):
            item = {'name': random.choice(items), 'cost': float(random.randint(50, 5000))}
            itemlist.append(item)
        InsertData.insertBill(admissionID, total_owed, total_paid, insurance_paid, itemlist)
        if random.random() < 0.7:
            UpdateDB.admissionUpdateDischarge(admissionID, admit_date + timedelta(days=random.randint(1, 30)), encryptionKey)

# --- Execute Data Generation ---
if __name__ == "__main__":

    keys = EncryptionKey.getKeys()

    populate_users(keys[0], keys[1], 50)          # 50 users
    populate_patients(keys[0], keys[1], 200)      # 200 patients
    populate_admissions(keys[0], keys[1], 250)    # 250 admissions
    print("Dummy data generation complete!")