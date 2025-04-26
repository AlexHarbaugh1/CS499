# CS499
Patient Information Management System

hospitalDB.py
-----------------------------------
**REQUIREMENTS**
Install and setup PostgreSQL Version 17.2
Found Here: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
During Setup it will ask for you to set a password, the password I use is 49910.
If you use a different password edit the Password fields in the code to your personal password.
Optional:
During installation there are additional applications for install.
pgAdmin4 gives tools for visualizing and managing the database outside of the code editor.

Psycopg2 Library for Python
Install by running in your terminal: pip3 install psycopg2
Recommended:
SQLTools is an extension for VSCode that allows you to pass SQL commands directly to the database.
I use this to test that sql commands work before adding them to the python code.

CREATE Patient table requires access to the encryption keys to store the patients data.
Encryption Keys are stored in Hashicorp.
**REQUIREMENTS**
Create An Account Here: https://portal.cloud.hashicorp.com/sign-in
After Creating an account I can guide you through the process to use the API
Dependencies for using the API are:
jq found here: https://jqlang.org/
hcp found here: https://releases.hashicorp.com/hcp/0.8.0/    --Download appropriate  version I used amd64

InsertData.py
------------------------------------

EncryptionKey.py
------------------------------------

GetApiKey.py
------------------------------------
=======
# Hospital Management System

A comprehensive hospital management solution with a focus on patient information security, RBAC (Role-Based Access Control), and audit logging.

## Features

- **Patient Management:** Register and manage patient information
- **Staff Management:** Register and manage staff with role-based access control
- **Admission Management:** Track patient admissions and discharges
- **Billing System:** Generate and track patient billing information
- **Prescription Management:** Manage patient medications and dosages
- **Procedure Scheduling:** Schedule and track medical procedures
- **Visitor Management:** Manage approved visitors for patients
- **Audit Logging:** Track all system activities for security and compliance
- **Database Encryption:** Secure sensitive patient and staff information
- **Role-Based Access:** Five different user roles with appropriate permissions

## System Requirements

### Server Installation
- Windows 10/11 or Windows Server 2016+
- 4GB RAM minimum (8GB recommended)
- PostgreSQL 14 or newer
- 500MB available disk space (plus database storage)
- Administrative privileges for installation

### Client Installation
- Windows 10/11
- 2GB RAM minimum
- Network connection to the server
- 200MB available disk space

## Installation Instructions

### Server Installation

1. Download the `HospitalManagementSystem_Setup.exe` installer
2. Run the installer with administrative privileges
3. Follow the installation wizard:
   - Choose "Server Installation" option
   - Configure PostgreSQL settings:
     - Installation directory
     - Port (default: 5432)
     - Admin username/password
   - Complete the installation

### Client Installation

1. Download the `HospitalManagementSystem_Setup.exe` installer
2. Run the installer with administrative privileges
3. Follow the installation wizard:
   - Choose "Client Installation" option
   - Enter the server IP address
   - Complete the installation

## First-Time Setup

### Server Setup

1. After installation, run the Hospital Management System from the desktop shortcut
2. The system will initialize and create the database automatically
3. You will be prompted to create the first administrator account:
   - Enter administrator's first and last name
   - Create a username and password
   - This account will have full access to the system

### Client Setup

1. After installation, run the Hospital Management System from the desktop shortcut
2. The system will connect to the server automatically (using the IP provided during installation)
3. Login with credentials provided by the administrator

## Usage Guide

### User Roles

The system supports five user roles with different permission levels:

1. **Administrator:**
   - Full system access
   - Create and manage user accounts
   - Register locations
   - Access audit logs

2. **Medical Personnel:**
   - Register patients
   - Register admissions
   - Add/view notes
   - Manage billing
   - View patient details

3. **Physician:**
   - All Medical Personnel permissions
   - Order prescriptions
   - Schedule procedures
   - Manage billing
   - Add/view medical notes

4. **Office Staff:**
   - Register patients
   - Update patient information
   - Access non-medical data

5. **Volunteer:**
   - Limited access
   - View patient location
   - View approved visitors

### Common Tasks

#### Registering a Patient
1. Login with Administrator, Medical Personnel, Physician, or Office Staff credentials
2. Click "Register Patient"
3. Fill in the patient details (fields marked with * are required)
4. Click "Add Patient"

#### Searching for a Patient
1. Login with any account
2. Click "Patient Search"
3. Enter search criteria (first name, last name, or both)
4. Check "Partial Search" to find partial matches
5. Click "Search"
6. Double-click on a patient in the results to view details

#### Registering an Admission
1. Login with Medical Personnel, Physicianm or Administrator credentials
2. Click "Register Admission"
3. Select a patient, location, and doctor
4. Enter admission details
5. Click "Add Admission"

#### Adding Medical Notes
1. Login with Medical Personnel, Physicianm or Administrator credentials
2. Search for a patient
3. Navigate to the "Notes" tab
4. Enter your note in the text field
5. Click "Save Note"

#### Processing Payments
1. Login with Administrator, Physician, or Medical Personnel credentials
2. Search for a patient
3. Navigate to the "Billing" tab
4. Select a billing record
5. Click "Process Payment"
6. Enter payment details and confirm


## Troubleshooting

### Connection Issues
- Verify the server is running
- Check network connectivity
- Ensure the correct server IP is configured in client settings
- Verify PostgreSQL service is running on the server

### Login Issues
- Verify username and password
- Check that the user account is not locked
- Ensure proper database connectivity

### Database Errors
- Check PostgreSQL service status
- Verify database connectivity settings
- Ensure sufficient disk space
- Check for database file corruption
