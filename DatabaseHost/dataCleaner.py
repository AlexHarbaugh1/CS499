import hospitalDB
import datetime
import EncryptionKey
from InsertData import log_action
import sys
import logging

# Set up logging
logging.basicConfig(
    filename='database_cleanup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def cleanup_old_records(years_threshold=5):
    """
    Remove records from the database that are older than the specified threshold.
    By default, removes records older than 5 years.
    """
    try:
        logging.info(f"Starting cleanup process for records older than {years_threshold} years")
        
        # Initialize database connection
        hospitalDB.run()
        
        keys = EncryptionKey.getKeys()
        encryption_key = keys[0]
        
        with hospitalDB.get_cursor() as cursor:
            # Set role to administrator
            cursor.execute("SET ROLE administrator_role;")
            
            # Calculate the cutoff date
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=years_threshold * 365)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Find discharge dates for comparison
            sql = """SELECT admission_id 
                     FROM admission 
                     WHERE pgp_sym_decrypt(discharge_datetime, %s)::timestamp < %s::timestamp
                     AND discharge_datetime IS NOT NULL
                     AND pgp_sym_decrypt(discharge_datetime, %s) != 'None';"""
            params = (encryption_key, cutoff_date_str, encryption_key)
            cursor.execute(sql, params)
            old_admissions = cursor.fetchall()
            
            admission_count = len(old_admissions)
            
            if admission_count == 0:
                logging.info("No records found older than threshold. No cleanup needed.")
                return 0
            
            old_admission_ids = [admission[0] for admission in old_admissions]
            
            # Delete from dependent tables first
            
            # 1. Delete from BillingDetail
            sql = """DELETE FROM BillingDetail 
                     WHERE billing_id IN (
                         SELECT billing_id 
                         FROM Billing 
                         WHERE admission_id = ANY(%s)
                     );"""
            cursor.execute(sql, (old_admission_ids,))
            
            # 2. Delete from Billing
            sql = "DELETE FROM Billing WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 3. Delete from PatientNote
            sql = "DELETE FROM PatientNote WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 4. Delete from Prescription
            sql = "DELETE FROM Prescription WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 5. Delete from ScheduledProcedure
            sql = "DELETE FROM ScheduledProcedure WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 6. Delete from ApprovedVisitors
            sql = "DELETE FROM ApprovedVisitors WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 7. Delete from Admission table
            sql = "DELETE FROM Admission WHERE admission_id = ANY(%s);"
            cursor.execute(sql, (old_admission_ids,))
            
            # 8. Clean up old audit logs
            sql = """DELETE FROM auditlog 
                     WHERE timestamp < %s::timestamp;"""
            cursor.execute(sql, (cutoff_date_str,))
            
            # Set up user context for audit log
            cursor.execute("SET app.current_user = 'SYSTEM';")
            
            # Log the cleanup action
            log_action(f"System cleanup: Removed {admission_count} admission records and related data older than {years_threshold} years")
            
            logging.info(f"Successfully cleaned up {admission_count} admissions and related records.")
            return admission_count
            
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
        return 0

def main():
    """Main function to run cleanup"""
    try:
        records_cleaned = cleanup_old_records()
        print(f"Cleanup completed. {records_cleaned} records removed.")
        logging.info(f"Daily cleanup completed successfully. {records_cleaned} records removed.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        logging.error(f"Daily cleanup failed: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()