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
