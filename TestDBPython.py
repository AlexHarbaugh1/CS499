
import psycopg2

# connection establishment
conn = psycopg2.connect(
   database="postgres",
    user='postgres',
    password='49910',
    host='localhost',
    port= '5432'
)
 
conn.autocommit = True
 
# Creating a cursor object
cursor = conn.cursor()
cursor.execute("""SELECT EXISTS 
               (SELECT datname FROM pg_catalog.pg_database
               WHERE datname='huntsvillehospital')""")
if(not cursor.fetchone()[0]):
  cursor.execute("""CREATE DATABASE huntsvillehospital""")
  con2 = psycopg2.connect(
    database="huntsvillehospital",
    user='postgres',
    password='49910',
    host='localhost',
    port= '5432'
  )
  con2.autocommit = True
  cursor2 = con2.cursor()

  cursor2.execute("""CREATE TABLE Users (id serial PRIMARY KEY,
              username VARCHAR(255) NOT NULL UNIQUE,
              password VARCHAR(255) NOT NULL,
              firstname VARCHAR(255) NOT NULL,
              lastname VARCHAR(255) NOT NULL,
              type VARCHAR(255) CHECK (type IN ('Physician', 'Office Staff', 'Volunteer', 'Medical Personnel')) NOT NULL);"""
              )
  cursor2.execute("""CREATE TABLE Patients (id serial PRIMARY KEY,
              lastname VARCHAR(255) NOT NULL,
              firstname VARCHAR(255) NOT NULL,
              middlename VARCHAR(255),
              mailing_address VARCHAR(255),
              home_phone VARCHAR(10),
              work_phone VARCHAR(10),
              contact1_name VARCHAR(255),
              contact1_phone VARCHAR(10),
              contact2_name VARCHAR(255),
              contact2_phone VARCHAR(10),
              family_doctor VARCHAR(255),
              insurance_carrier VARCHAR(255),
              insurance_account VARCHAR(255),
              insurance_group_number VARCHAR(255),
              billing_information TEXT,
              amount_paid VARCHAR(12),
              amount_owed VARCHAR(12),
              amount_paid_insurance VARCHAR(12)      
              );"""
              )
  print("Database Created")
else:
  print("Database Already Exists")

# Closing the connection
conn.close()


