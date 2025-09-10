import sqlite3
from datetime import datetime, date
import os
from sql_fin_exp import InsuranceClaimsDatabase

class InsuranceClaimsDatabase:
    def __init__(self, db_name="insurance_claims.db"):
        """Initialize the Insurance Claims Database"""
        self.db_name = db_name
        # Remove existing database to start fresh
        if os.path.exists(db_name):
            os.remove(db_name)

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        """Create all required tables for the insurance claims system"""

        print("Creating database tables...")

        # Policies Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS POLICIES (
                policy_id TEXT PRIMARY KEY,
                policy_type TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                base_sum_insured REAL,
                policy_period_days INTEGER,
                territory TEXT,
                created_date DATE DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'ACTIVE'
            )
        """)

        # Coverage Types Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS COVERAGE_TYPES (
                coverage_id TEXT PRIMARY KEY,
                coverage_name TEXT NOT NULL,
                coverage_type TEXT NOT NULL,
                description TEXT,
                min_age INTEGER DEFAULT 0,
                max_age INTEGER DEFAULT 99,
                waiting_period_days INTEGER DEFAULT 0,
                policy_tenure_months INTEGER DEFAULT 12
            )
        """)

        # Insured Persons Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS INSURED_PERSONS (
                insured_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                city TEXT,
                state TEXT,
                policy_id TEXT,
                policy_start_date DATE,
                policy_end_date DATE,
                status TEXT DEFAULT 'ACTIVE',
                FOREIGN KEY (policy_id) REFERENCES POLICIES(policy_id)
            )
        """)

        # Claims Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CLAIMS (
                claim_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                insured_id TEXT NOT NULL,
                coverage_id TEXT NOT NULL,
                status TEXT DEFAULT 'SUBMITTED',
                claim_date DATE,
                claim_amount REAL,
                approved_amount REAL DEFAULT 0,
                description TEXT,
                incident_date DATE,
                incident_location TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (policy_id) REFERENCES POLICIES(policy_id),
                FOREIGN KEY (insured_id) REFERENCES INSURED_PERSONS(insured_id),
                FOREIGN KEY (coverage_id) REFERENCES COVERAGE_TYPES(coverage_id)
            )
        """)

        # Medical Procedures Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MEDICAL_PROCEDURES (
                procedure_id TEXT PRIMARY KEY,
                procedure_name TEXT NOT NULL,
                category TEXT,
                procedure_type TEXT,
                is_covered BOOLEAN,
                waiting_period_days INTEGER DEFAULT 0,
                notes TEXT
            )
        """)

        # Exclusions Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS EXCLUSIONS (
                exclusion_id TEXT PRIMARY KEY,
                exclusion_name TEXT NOT NULL,
                exclusion_type TEXT,
                description TEXT,
                applicable_coverage TEXT,
                severity TEXT
            )
        """)

        # Policy Rules Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS POLICY_RULES (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                rule_type TEXT,
                coverage_id TEXT,
                rule_condition TEXT,
                rule_result TEXT,
                priority INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)

        # Required Documents Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS REQUIRED_DOCUMENTS (
                document_id TEXT PRIMARY KEY,
                coverage_id TEXT,
                document_name TEXT NOT NULL,
                is_mandatory BOOLEAN DEFAULT TRUE,
                description TEXT
            )
        """)

        # Claim Documents Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CLAIM_DOCUMENTS (
                claim_id TEXT,
                document_id TEXT,
                submission_date DATE,
                status TEXT DEFAULT 'PENDING',
                notes TEXT,
                PRIMARY KEY (claim_id, document_id)
            )
        """)

        # Medical Providers Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MEDICAL_PROVIDERS (
                provider_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                city TEXT,
                state TEXT,
                is_network TEXT DEFAULT 'No',
                rating TEXT,
                contact_info TEXT
            )
        """)

        # Claim Assessments Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CLAIM_ASSESSMENTS (
                assessment_id TEXT PRIMARY KEY,
                claim_id TEXT,
                assessor_id TEXT,
                assessment_date DATE,
                status TEXT,
                recommended_amount REAL,
                approved_amount REAL,
                remarks TEXT
            )
        """)

        # Claim History Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CLAIM_HISTORY (
                history_id TEXT PRIMARY KEY,
                claim_id TEXT,
                status_from TEXT,
                status_to TEXT,
                changed_by TEXT,
                change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                remarks TEXT
            )
        """)

        # Pre-existing Conditions Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS PREEXISTING_CONDITIONS (
                condition_id TEXT PRIMARY KEY,
                insured_id TEXT,
                condition_name TEXT,
                diagnosed_date DATE,
                severity TEXT,
                is_disclosed BOOLEAN DEFAULT FALSE,
                treatment_history TEXT
            )
        """)

        print("✅ All tables created successfully!")

    def insert_sample_data(self):
        """Insert comprehensive sample data"""

        print("Starting data insertion...")

        # Insert Policies
        policies_data = [
            ('CHOTGDP23004V012223', 'Group Domestic Travel Insurance',
             'Cholamandalam MS General Insurance - Group Domestic Travel', 0, 365, 'India'),
            ('EDLHLGP21462V032021', 'Health Insurance Base Policy',
             'Edelweiss General Insurance - Health Insurance Base', 0, 365, 'India'),
            ('EDLHLGA23009V012223', 'Well Baby Well Mother Add-On',
             'Edelweiss General Insurance - Maternity and Newborn Care', 0, 365, 'India'),
            ('CHOTGDP23004V032021', 'Individual Travel Insurance',
             'Cholamandalam MS General Insurance - Individual Travel', 0, 365, 'India'),
            ('CHOTGDP23004V042021', 'Family Travel Insurance',
             'Cholamandalam MS General Insurance - Family Travel', 0, 365, 'India')
        ]

        for policy in policies_data:
            self.cursor.execute("""
                INSERT INTO POLICIES (policy_id, policy_type, policy_name, base_sum_insured, policy_period_days, territory)
                VALUES (?, ?, ?, ?, ?, ?)
            """, policy)
        print("✅ Policies inserted (5 records)")

        # Insert Coverage Types
        coverage_data = [
            # Base Covers
            ('BASE_001', 'Emergency Accidental Hospitalization', 'BASE',
             'Medical expenses for accidental injury during travel', 0, 90, 0, 12),
            ('BASE_002', 'OPD Treatment', 'BASE',
             'Out-patient treatment for accidental injury', 0, 90, 0, 12),
            ('BASE_003', 'Personal Accident - Accidental Death', 'BASE',
             'Compensation for accidental death', 0, 90, 0, 12),
            ('BASE_004', 'Personal Accident - Permanent Total Disability', 'BASE',
             'Compensation for permanent total disability', 0, 90, 0, 12),
            ('BASE_005', 'Personal Accident - Permanent Partial Disability', 'BASE',
             'Compensation for permanent partial disability', 0, 90, 0, 12),

            # Optional Covers
            ('OPT_001', 'Emergency Medical Expenses - Illness/Disease', 'OPTIONAL',
             'Medical expenses for illness not related to medical history', 0, 90, 0, 12),
            ('OPT_002', 'Emergency Medical Evacuation & Repatriation', 'OPTIONAL',
             'Transportation and repatriation costs', 0, 90, 0, 12),
            ('OPT_003', 'Pre-existing Condition in Life Threatening Situation', 'OPTIONAL',
             'Coverage for pre-existing conditions in emergencies', 0, 90, 0, 12),
            ('OPT_004', 'Personal Accident - Common Carrier', 'OPTIONAL',
             'Additional PA coverage in common carrier', 0, 90, 0, 12),
            ('OPT_005', 'Dental Treatment Expenses', 'OPTIONAL',
             'Dental treatment from accidental injury', 0, 90, 0, 12),
            ('OPT_006', 'Daily Allowance - Hospitalization', 'OPTIONAL',
             'Fixed daily allowance during hospitalization', 0, 90, 0, 12),
            ('OPT_011', 'Total Loss of Checked-in Baggage', 'OPTIONAL',
             'Compensation for total baggage loss by airlines', 0, 90, 0, 12),
            ('OPT_013', 'Trip Cancellation', 'OPTIONAL',
             'Reimbursement for trip cancellation', 0, 90, 0, 12),
            ('OPT_014', 'Trip Interruption', 'OPTIONAL',
             'Reimbursement for trip interruption', 0, 90, 0, 12),
            ('OPT_018', 'Flight Delay', 'OPTIONAL',
             'Compensation for flight delays', 0, 90, 0, 12),

            # Edelweiss Covers
            ('EDL_001', 'Air Ambulance Cover', 'OPTIONAL',
             'Emergency air ambulance for life-threatening conditions', 0, 99, 0, 12),
            ('EDL_002', 'Well Mother Cover - Option 1', 'OPTIONAL',
             'Routine medical care during pregnancy', 18, 50, 0, 9),
            ('EDL_003', 'Well Mother Cover - Option 2', 'OPTIONAL',
             'Pregnancy care including hospitalization', 18, 50, 0, 9),
            ('EDL_004', 'Well Mother Cover - Option 3', 'OPTIONAL',
             'Complete pregnancy care including post-delivery', 18, 50, 0, 10),
            ('EDL_005', 'Well Baby Care', 'OPTIONAL',
             'Newborn care from birth to hospital discharge', 0, 1, 0, 1)
        ]

        for coverage in coverage_data:
            self.cursor.execute("""
                INSERT INTO COVERAGE_TYPES 
                (coverage_id, coverage_name, coverage_type, description, min_age, max_age, waiting_period_days, policy_tenure_months)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, coverage)
        print("✅ Coverage types inserted (20 records)")

        # Insert Insured Persons
        insured_data = [
            ('INS_001', 'Rajesh Kumar', '1985-03-15', 'Male', 'Mumbai', 'Maharashtra', 'CHOTGDP23004V012223',
             '2024-01-01', '2024-12-31', 'ACTIVE'),
            ('INS_002', 'Priya Sharma', '1990-07-22', 'Female', 'Delhi', 'Delhi', 'CHOTGDP23004V012223', '2024-01-15',
             '2025-01-14', 'ACTIVE'),
            ('INS_003', 'Amit Patel', '1982-11-08', 'Male', 'Ahmedabad', 'Gujarat', 'CHOTGDP23004V012223', '2024-02-01',
             '2025-01-31', 'ACTIVE'),
            ('INS_004', 'Sunita Reddy', '1988-05-30', 'Female', 'Hyderabad', 'Telangana', 'CHOTGDP23004V012223',
             '2024-02-15', '2025-02-14', 'ACTIVE'),
            ('INS_005', 'Vikram Singh', '1975-09-12', 'Male', 'Jaipur', 'Rajasthan', 'CHOTGDP23004V012223',
             '2024-03-01', '2025-02-28', 'ACTIVE'),
            ('INS_006', 'Kavya Iyer', '1992-12-25', 'Female', 'Chennai', 'Tamil Nadu', 'EDLHLGA23009V012223',
             '2024-01-01', '2024-12-31', 'ACTIVE'),
            ('INS_007', 'Neha Gupta', '1987-04-18', 'Female', 'Pune', 'Maharashtra', 'EDLHLGA23009V012223',
             '2024-01-15', '2025-01-14', 'ACTIVE'),
            ('INS_008', 'Ritu Jain', '1991-08-03', 'Female', 'Indore', 'Madhya Pradesh', 'EDLHLGA23009V012223',
             '2024-02-01', '2025-01-31', 'ACTIVE'),
            ('INS_009', 'Anita Malhotra', '1989-06-14', 'Female', 'Chandigarh', 'Punjab', 'EDLHLGA23009V012223',
             '2024-02-15', '2025-02-14', 'ACTIVE'),
            ('INS_010', 'Pooja Agarwal', '1993-10-27', 'Female', 'Kolkata', 'West Bengal', 'EDLHLGA23009V012223',
             '2024-03-01', '2025-02-28', 'ACTIVE'),
            ('INS_011', 'Manish Khanna', '1980-01-09', 'Male', 'Lucknow', 'Uttar Pradesh', 'CHOTGDP23004V012223',
             '2024-03-15', '2025-03-14', 'ACTIVE'),
            ('INS_012', 'Deepak Nair', '1986-03-21', 'Male', 'Kochi', 'Kerala', 'CHOTGDP23004V012223', '2024-04-01',
             '2025-03-31', 'ACTIVE'),
            ('INS_013', 'Sanjay Rao', '1984-07-16', 'Male', 'Bangalore', 'Karnataka', 'CHOTGDP23004V012223',
             '2024-04-15', '2025-04-14', 'ACTIVE'),
            ('INS_014', 'Rekha Pandey', '1979-02-28', 'Female', 'Bhopal', 'Madhya Pradesh', 'CHOTGDP23004V012223',
             '2024-05-01', '2025-04-30', 'ACTIVE'),
            ('INS_015', 'Arjun Mehta', '1983-12-05', 'Male', 'Surat', 'Gujarat', 'CHOTGDP23004V012223', '2024-05-15',
             '2025-05-14', 'ACTIVE'),
            ('INS_016', 'Shweta Kapoor', '1990-09-11', 'Female', 'Noida', 'Uttar Pradesh', 'EDLHLGA23009V012223',
             '2024-03-15', '2025-03-14', 'ACTIVE'),
            ('INS_017', 'Meera Prasad', '1988-11-23', 'Female', 'Patna', 'Bihar', 'EDLHLGA23009V012223', '2024-04-01',
             '2025-03-31', 'ACTIVE'),
            ('INS_018', 'Divya Saxena', '1994-01-17', 'Female', 'Gwalior', 'Madhya Pradesh', 'EDLHLGA23009V012223',
             '2024-04-15', '2025-04-14', 'ACTIVE'),
            ('INS_019', 'Geeta Verma', '1985-05-08', 'Female', 'Agra', 'Uttar Pradesh', 'EDLHLGA23009V012223',
             '2024-05-01', '2025-04-30', 'ACTIVE'),
            ('INS_020', 'Seema Joshi', '1991-07-30', 'Female', 'Nashik', 'Maharashtra', 'EDLHLGA23009V012223',
             '2024-05-15', '2025-05-14', 'ACTIVE'),
            ('INS_021', 'Rohit Desai', '1982-04-12', 'Male', 'Vadodara', 'Gujarat', 'CHOTGDP23004V032021', '2024-06-01',
             '2025-05-31', 'ACTIVE'),
            ('INS_022', 'Kiran Bose', '1987-08-24', 'Male', 'Siliguri', 'West Bengal', 'CHOTGDP23004V032021',
             '2024-06-15', '2025-06-14', 'ACTIVE'),
            ('INS_023', 'Alok Tripathi', '1981-10-06', 'Male', 'Varanasi', 'Uttar Pradesh', 'CHOTGDP23004V032021',
             '2024-07-01', '2025-06-30', 'ACTIVE'),
            ('INS_024', 'Smita Kulkarni', '1989-02-14', 'Female', 'Nagpur', 'Maharashtra', 'CHOTGDP23004V032021',
             '2024-07-15', '2025-07-14', 'ACTIVE'),
            ('INS_025', 'Ravi Chatterjee', '1983-06-19', 'Male', 'Durgapur', 'West Bengal', 'CHOTGDP23004V032021',
             '2024-08-01', '2025-07-31', 'ACTIVE'),
            ('INS_026', 'Anjali Verma', '1990-03-12', 'Female', 'Jaipur', 'Rajasthan', 'EDLHLGA23009V012223',
             '2024-01-20', '2025-01-19', 'ACTIVE'),
            ('INS_027', 'Sanjay Gupta', '1985-06-18', 'Male', 'Kanpur', 'Uttar Pradesh', 'CHOTGDP23004V012223',
             '2024-02-10', '2025-02-09', 'ACTIVE'),
            ('INS_028', 'Kavita Sharma', '1988-09-25', 'Female', 'Indore', 'Madhya Pradesh', 'EDLHLGA23009V012223',
             '2024-03-05', '2025-03-04', 'ACTIVE'),
            ('INS_029', 'Rahul Mishra', '1984-12-08', 'Male', 'Patna', 'Bihar', 'CHOTGDP23004V012223', '2024-04-12',
             '2025-04-11', 'ACTIVE'),
            ('INS_030', 'Sunita Singh', '1992-11-15', 'Female', 'Lucknow', 'Uttar Pradesh', 'EDLHLGA23009V012223',
             '2024-05-08', '2025-05-07', 'ACTIVE')
        ]

        for insured in insured_data:
            self.cursor.execute("""
                INSERT INTO INSURED_PERSONS 
                (insured_id, name, date_of_birth, gender, city, state, policy_id, policy_start_date, policy_end_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insured)
        print("✅ Insured persons inserted (30 records)")

        # Insert Claims
        claims_data = [
            ('CLM_001', 'CHOTGDP23004V012223', 'INS_001', 'BASE_001', 'APPROVED',
             '2024-03-15', 25000.00, 25000.00, 'Accidental injury during travel in Mumbai', '2024-03-14',
             'Mumbai, Maharashtra'),
            ('CLM_002', 'CHOTGDP23004V012223', 'INS_002', 'BASE_003', 'APPROVED',
             '2024-03-20', 500000.00, 500000.00, 'Accidental death during travel', '2024-03-19', 'Delhi, Delhi'),
            ('CLM_003', 'CHOTGDP23004V012223', 'INS_003', 'OPT_001', 'UNDER_REVIEW',
             '2024-03-25', 15000.00, 0.00, 'Emergency illness treatment', '2024-03-24', 'Ahmedabad, Gujarat'),
            ('CLM_004', 'CHOTGDP23004V012223', 'INS_004', 'OPT_011', 'REJECTED',
             '2024-04-01', 8000.00, 0.00, 'Baggage loss not meeting policy criteria', '2024-03-31',
             'Hyderabad, Telangana'),
            ('CLM_005', 'CHOTGDP23004V012223', 'INS_005', 'BASE_004', 'APPROVED',
             '2024-04-05', 300000.00, 300000.00, 'Permanent total disability from accident', '2024-04-04',
             'Jaipur, Rajasthan'),
            ('CLM_006', 'EDLHLGA23009V012223', 'INS_006', 'EDL_001', 'UNDER_REVIEW',
             '2024-04-10', 45000.00, 0.00, 'Air ambulance service for emergency delivery', '2024-04-09',
             'Chennai, Tamil Nadu'),
            ('CLM_007', 'EDLHLGA23009V012223', 'INS_007', 'EDL_002', 'APPROVED',
             '2024-04-15', 12000.00, 12000.00, 'Routine prenatal care expenses', '2024-04-14', 'Pune, Maharashtra'),
            ('CLM_008', 'EDLHLGA23009V012223', 'INS_008', 'EDL_005', 'APPROVED',
             '2024-04-20', 8000.00, 8000.00, 'Newborn care during hospital stay', '2024-04-19',
             'Indore, Madhya Pradesh'),
            ('CLM_009', 'EDLHLGA23009V012223', 'INS_009', 'EDL_003', 'APPROVED',
             '2024-04-25', 18000.00, 18000.00, 'Maternity care including hospitalization', '2024-04-24',
             'Chandigarh, Punjab'),
            ('CLM_010', 'EDLHLGA23009V012223', 'INS_010', 'EDL_004', 'SUBMITTED',
             '2024-05-01', 22000.00, 0.00, 'Complete pregnancy care including post-delivery', '2024-04-30',
             'Kolkata, West Bengal'),
            ('CLM_011', 'CHOTGDP23004V012223', 'INS_011', 'OPT_002', 'APPROVED',
             '2024-05-05', 35000.00, 35000.00, 'Medical evacuation from remote area', '2024-05-04',
             'Lucknow, Uttar Pradesh'),
            ('CLM_012', 'CHOTGDP23004V012223', 'INS_012', 'OPT_003', 'REJECTED',
             '2024-05-10', 20000.00, 0.00, 'Pre-existing condition not life-threatening', '2024-05-09',
             'Kochi, Kerala'),
            ('CLM_013', 'CHOTGDP23004V012223', 'INS_013', 'OPT_005', 'APPROVED',
             '2024-05-15', 5000.00, 5000.00, 'Emergency dental treatment after accident', '2024-05-14',
             'Bangalore, Karnataka'),
            ('CLM_014', 'CHOTGDP23004V012223', 'INS_014', 'OPT_013', 'UNDER_REVIEW',
             '2024-05-20', 12000.00, 0.00, 'Trip cancellation due to family emergency', '2024-05-19',
             'Bhopal, Madhya Pradesh'),
            ('CLM_015', 'CHOTGDP23004V012223', 'INS_015', 'OPT_018', 'APPROVED',
             '2024-05-25', 3000.00, 3000.00, 'Flight delay compensation', '2024-05-24', 'Surat, Gujarat'),
            ('CLM_016', 'EDLHLGA23009V012223', 'INS_016', 'EDL_001', 'REJECTED',
             '2024-06-01', 50000.00, 0.00, 'Air ambulance distance exceeded limit', '2024-05-31',
             'Noida, Uttar Pradesh'),
            ('CLM_017', 'EDLHLGA23009V012223', 'INS_017', 'EDL_002', 'APPROVED',
             '2024-06-05', 9500.00, 9500.00, 'Prenatal diagnostic tests and consultations', '2024-06-04',
             'Patna, Bihar'),
            ('CLM_018', 'EDLHLGA23009V012223', 'INS_018', 'EDL_005', 'APPROVED',
             '2024-06-10', 6500.00, 6500.00, 'Newborn immunizations and examinations', '2024-06-09',
             'Gwalior, Madhya Pradesh'),
            ('CLM_019', 'EDLHLGA23009V012223', 'INS_019', 'EDL_003', 'UNDER_REVIEW',
             '2024-06-15', 15500.00, 0.00, 'Maternity care with complications', '2024-06-14', 'Agra, Uttar Pradesh'),
            ('CLM_020', 'EDLHLGA23009V012223', 'INS_020', 'EDL_004', 'APPROVED',
             '2024-06-20', 25000.00, 25000.00, 'Complete maternity care including postnatal', '2024-06-19',
             'Nashik, Maharashtra'),
            ('CLM_021', 'CHOTGDP23004V032021', 'INS_021', 'BASE_001', 'SUBMITTED',
             '2024-06-25', 18000.00, 0.00, 'Emergency hospitalization due to food poisoning', '2024-06-24',
             'Vadodara, Gujarat'),
            ('CLM_022', 'CHOTGDP23004V032021', 'INS_022', 'BASE_005', 'APPROVED',
             '2024-07-01', 75000.00, 75000.00, 'Partial disability compensation', '2024-06-30',
             'Siliguri, West Bengal'),
            ('CLM_023', 'CHOTGDP23004V032021', 'INS_023', 'OPT_006', 'APPROVED',
             '2024-07-05', 4000.00, 4000.00, 'Daily allowance during hospitalization', '2024-07-04',
             'Varanasi, Uttar Pradesh'),
            ('CLM_024', 'CHOTGDP23004V032021', 'INS_024', 'OPT_014', 'REJECTED',
             '2024-07-10', 15000.00, 0.00, 'Trip interruption not covered under policy terms', '2024-07-09',
             'Nagpur, Maharashtra'),
            ('CLM_025', 'CHOTGDP23004V032021', 'INS_025', 'OPT_011', 'APPROVED',
             '2024-07-15', 12000.00, 12000.00, 'Total loss of checked baggage', '2024-07-14', 'Durgapur, West Bengal'),
            ('CLM_026', 'EDLHLGA23009V012223', 'INS_026', 'EDL_003', 'APPROVED',
             '2024-07-20', 16500.00, 16500.00, 'Maternity hospitalization with routine care', '2024-07-19',
             'Jaipur, Rajasthan'),
            ('CLM_027', 'EDLHLGA23009V012223', 'INS_028', 'EDL_001', 'UNDER_REVIEW',
             '2024-07-25', 42000.00, 0.00, 'Air ambulance for pregnancy complications', '2024-07-24',
             'Indore, Madhya Pradesh'),
            ('CLM_028', 'EDLHLGA23009V012223', 'INS_030', 'EDL_005', 'APPROVED',
             '2024-08-01', 7200.00, 7200.00, 'Newborn care and preventive services', '2024-07-31',
             'Lucknow, Uttar Pradesh'),
            # Continuation of the previous file - add this to the claims_data list

            ('CLM_029', 'CHOTGDP23004V012223', 'INS_027', 'BASE_002', 'APPROVED',
             '2024-08-05', 3500.00, 3500.00, 'OPD treatment for accidental injury', '2024-08-04',
             'Kanpur, Uttar Pradesh'),
            ('CLM_030', 'CHOTGDP23004V012223', 'INS_029', 'OPT_011', 'APPROVED',
             '2024-08-10', 2800.00, 2800.00, 'Emergency purchases due to baggage delay', '2024-08-09', 'Patna, Bihar'),
            ('CLM_031', 'CHOTGDP23004V012223', 'INS_001', 'OPT_006', 'APPROVED',
             '2024-08-15', 2000.00, 2000.00, 'Daily allowance during hospitalization', '2024-08-14',
             'Mumbai, Maharashtra'),
            ('CLM_032', 'EDLHLGA23009V012223', 'INS_007', 'EDL_004', 'APPROVED',
             '2024-08-20', 21500.00, 21500.00, 'Complete pregnancy care including post-delivery', '2024-08-19',
             'Pune, Maharashtra'),
            ('CLM_033', 'CHOTGDP23004V012223', 'INS_011', 'OPT_004', 'APPROVED',
             '2024-08-25', 150000.00, 150000.00, 'Personal accident in common carrier', '2024-08-24',
             'Lucknow, Uttar Pradesh'),
            ('CLM_034', 'EDLHLGA23009V012223', 'INS_016', 'EDL_003', 'UNDER_REVIEW',
             '2024-08-30', 17800.00, 0.00, 'Maternity care with extended hospitalization', '2024-08-29',
             'Noida, Uttar Pradesh'),
            ('CLM_035', 'CHOTGDP23004V012223', 'INS_013', 'OPT_018', 'APPROVED',
             '2024-09-05', 5500.00, 5500.00, 'Flight delay due to weather conditions', '2024-09-04',
             'Bangalore, Karnataka'),
            ('CLM_036', 'CHOTGDP23004V032021', 'INS_021', 'BASE_003', 'UNDER_REVIEW',
             '2024-09-10', 400000.00, 0.00, 'Accidental death claim under investigation', '2024-09-09',
             'Vadodara, Gujarat'),
            ('CLM_037', 'EDLHLGA23009V012223', 'INS_026', 'EDL_005', 'APPROVED',
             '2024-09-15', 8800.00, 8800.00, 'Newborn care with special medical attention', '2024-09-14',
             'Jaipur, Rajasthan'),
            ('CLM_038', 'CHOTGDP23004V012223', 'INS_015', 'OPT_013', 'APPROVED',
             '2024-09-20', 15000.00, 15000.00, 'Trip cancellation due to medical emergency', '2024-09-19',
             'Surat, Gujarat'),
            ('CLM_039', 'CHOTGDP23004V032021', 'INS_024', 'BASE_001', 'APPROVED',
             '2024-09-25', 22000.00, 22000.00, 'Emergency hospitalization during travel', '2024-09-24',
             'Nagpur, Maharashtra'),
            ('CLM_040', 'EDLHLGA23009V012223', 'INS_028', 'EDL_002', 'SUBMITTED',
             '2024-09-30', 13500.00, 0.00, 'Prenatal care during second trimester', '2024-09-29',
             'Indore, Madhya Pradesh')
        ]

        for claim in claims_data:
            self.cursor.execute("""
                            INSERT INTO CLAIMS 
                            (claim_id, policy_id, insured_id, coverage_id, status, claim_date, claim_amount, 
                             approved_amount, description, incident_date, incident_location)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, claim)
        print("✅ Claims inserted (40 records)")

        # Insert Medical Procedures
        procedures_data = [
            ('PROC_001', 'Knee Surgery', 'Orthopedic', 'Accidental', True, 0, 'Covered only if due to accident'),
            ('PROC_002', 'Heart Surgery', 'Cardiac', 'Medical', True, 0, 'Emergency only'),
            ('PROC_003', 'Dental Treatment', 'Dental', 'Accidental', True, 0, 'Only for accidental injury'),
            ('PROC_004', 'Cosmetic Surgery', 'Cosmetic', 'Elective', False, 0,
             'Not covered unless medically necessary'),
            ('PROC_005', 'Physiotherapy', 'Rehabilitation', 'Medical', True, 0, 'Covered during hospitalization'),
            ('PROC_006', 'X-Ray', 'Diagnostic', 'Medical', True, 0, 'Covered during hospitalization'),
            ('PROC_007', 'Emergency Root Canal', 'Dental', 'Emergency', True, 0, 'Covered as OPD treatment'),
            ('PROC_008', 'MRI Scan', 'Diagnostic', 'Medical', True, 0, 'Covered for accident-related injuries'),
            ('PROC_009', 'CT Scan', 'Diagnostic', 'Medical', True, 0, 'Covered for accident-related injuries'),
            ('PROC_010', 'Blood Tests', 'Diagnostic', 'Medical', True, 0, 'Covered during treatment'),
            ('PROC_011', 'Air Ambulance Transport', 'Emergency Transport', 'Emergency', True, 0,
             'Maximum 150km distance'),
            ('PROC_012', 'Prenatal Care', 'Maternity', 'Routine', True, 0, 'Routine medical care during pregnancy'),
            ('PROC_013', 'Maternity Hospitalization', 'Maternity', 'Medical', True, 0, 'Care during maternity stay'),
            ('PROC_014', 'Postnatal Care', 'Maternity', 'Routine', True, 0, 'Up to 30 days post-delivery'),
            ('PROC_015', 'Newborn Examination', 'Pediatric', 'Routine', True, 0, 'Routine newborn examinations'),
            ('PROC_016', 'Newborn Immunizations', 'Pediatric', 'Preventive', True, 0, 'Routine immunizations'),
            ('PROC_017', 'Prenatal Diagnostics', 'Maternity', 'Diagnostic', True, 0,
             'Diagnostic tests during pregnancy'),
            ('PROC_018', 'Infertility Treatment', 'Reproductive', 'Elective', False, 0,
             'Not covered under maternity policy'),
            ('PROC_019', 'Pregnancy Pharmacy', 'Maternity', 'Medical', True, 0,
             'Prescribed medications during pregnancy'),
            ('PROC_020', 'Doctor Consultations - Maternity', 'Maternity', 'Medical', True, 0, 'Routine doctor visits')
        ]

        for procedure in procedures_data:
            self.cursor.execute("""
                            INSERT INTO MEDICAL_PROCEDURES 
                            (procedure_id, procedure_name, category, procedure_type, is_covered, waiting_period_days, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, procedure)
        print("✅ Medical procedures inserted (20 records)")

        # Insert Required Documents
        documents_data = [
            ('DOC_001', 'ALL', 'Identity Proof', True, 'Valid government issued identity document'),
            ('DOC_002', 'ALL', 'Address Proof', True, 'Valid address verification document'),
            ('DOC_003', 'ALL', 'Policy Certificate Copy', True, 'Copy of insurance policy certificate'),
            ('DOC_004', 'ALL', 'Claim Form', True, 'Duly filled and signed claim form'),
            ('DOC_005', 'ALL', 'Bank Account Details', True, 'Bank account information for claim settlement'),
            ('DOC_006', 'BASE_001', 'Medical Reports', True, 'Hospital reports with diagnosis and treatment'),
            ('DOC_007', 'BASE_001', 'Hospital Bills', True, 'Original bills with service descriptions'),
            ('DOC_008', 'BASE_001', 'FIR/MLC Copy', True, 'Police report for accidents in public places'),
            ('DOC_009', 'BASE_003', 'Death Certificate', True, 'Certificate clearly stating reason of death'),
            ('DOC_010', 'BASE_003', 'Post Mortem Report', True, 'Required in case of accidental death'),
            ('DOC_011', 'BASE_004,BASE_005', 'Disability Certificate', True, 'Certificate from civil surgeon'),
            ('DOC_012', 'OPT_011', 'Property Irregularity Report', True, 'PIR from airline for baggage loss'),
            ('DOC_013', 'OPT_005', 'Dental Records', True, 'Diagnosis and treatment details from dentist'),
            ('DOC_014', 'ALL', 'Travel Tickets', True, 'Proof of travel during policy period'),
            ('DOC_015', 'EDL_001', 'Medical Practitioner Certificate', True,
             'Certification of life-threatening condition'),
            ('DOC_016', 'EDL_001', 'Air Ambulance License', True, 'Proof of air ambulance provider license'),
            ('DOC_017', 'EDL_001', 'Distance Travel Proof', True, 'Documentation showing actual distance'),
            ('DOC_018', 'EDL_002,EDL_003,EDL_004', 'Pregnancy Confirmation', True, 'Medical confirmation of pregnancy'),
            ('DOC_019', 'EDL_002,EDL_003,EDL_004', 'Doctor Consultation Bills', True,
             'Bills for routine consultations'),
            ('DOC_020', 'EDL_005', 'Birth Certificate', True, 'Official birth certificate of newborn'),
            ('DOC_021', 'EDL_005', 'Newborn Medical Records', True, 'Medical records for newborn care'),
            ('DOC_022', 'OPT_013,OPT_014', 'Trip Booking Confirmation', True, 'Original booking confirmation'),
            ('DOC_023', 'OPT_018', 'Flight Delay Certificate', True, 'Official delay certificate from airline'),
            ('DOC_024', 'OPT_002', 'Medical Evacuation Authorization', True, 'Pre-authorization for evacuation'),
            ('DOC_025', 'OPT_006', 'Hospitalization Certificate', True, 'Certificate confirming hospitalization period')
        ]

        for document in documents_data:
            self.cursor.execute("""
                            INSERT INTO REQUIRED_DOCUMENTS 
                            (document_id, coverage_id, document_name, is_mandatory, description)
                            VALUES (?, ?, ?, ?, ?)
                        """, document)
        print("✅ Required documents inserted (25 records)")

        # Insert Medical Providers
        providers_data = [
            ('PROV_001', 'Apollo Hospital', 'HOSPITAL', 'Mumbai', 'Maharashtra', 'Yes', 'A+', '+91-22-26926666'),
            ('PROV_002', 'Fortis Healthcare', 'HOSPITAL', 'Delhi', 'Delhi', 'Yes', 'A+', '+91-11-47135000'),
            ('PROV_003', 'Manipal Hospital', 'HOSPITAL', 'Bangalore', 'Karnataka', 'Yes', 'A', '+91-80-25022000'),
            ('PROV_004', 'Max Healthcare', 'HOSPITAL', 'Gurgaon', 'Haryana', 'Yes', 'A+', '+91-124-4511111'),
            ('PROV_005', 'AIIMS', 'HOSPITAL', 'Delhi', 'Delhi', 'No', 'A+', '+91-11-26588500'),
            ('PROV_006', 'Air Rescue Services', 'AIR_AMBULANCE', 'Mumbai', 'Maharashtra', 'Yes', 'A+',
             '+91-22-28370000'),
            ('PROV_007', 'Sky Ambulance India', 'AIR_AMBULANCE', 'Delhi', 'Delhi', 'Yes', 'A+', '+91-11-41111111'),
            ('PROV_008', 'Dr. Rajesh Kumar', 'DOCTOR', 'Mumbai', 'Maharashtra', 'Yes', 'A', '+91-22-26567001'),
            ('PROV_009', 'Dr. Priya Sharma', 'DOCTOR', 'Delhi', 'Delhi', 'Yes', 'A', '+91-11-26567002'),
            ('PROV_010', 'Dr. Amit Patel', 'DOCTOR', 'Ahmedabad', 'Gujarat', 'Yes', 'A', '+91-79-26567003'),
            ('PROV_011', 'Ruby Hall Clinic', 'HOSPITAL', 'Pune', 'Maharashtra', 'Yes', 'A', '+91-20-26127777'),
            ('PROV_012', 'Medanta Hospital', 'HOSPITAL', 'Gurgaon', 'Haryana', 'Yes', 'A+', '+91-124-4141414'),
            ('PROV_013', 'Lilavati Hospital', 'HOSPITAL', 'Mumbai', 'Maharashtra', 'Yes', 'A', '+91-22-26567777'),
            ('PROV_014', 'CMC Vellore', 'HOSPITAL', 'Vellore', 'Tamil Nadu', 'Yes', 'A+', '+91-416-2281000'),
            ('PROV_015', 'Narayana Health', 'HOSPITAL', 'Bangalore', 'Karnataka', 'Yes', 'A', '+91-80-22222200')
        ]

        for provider in providers_data:
            self.cursor.execute("""
                            INSERT INTO MEDICAL_PROVIDERS 
                            (provider_id, name, type, city, state, is_network, rating, contact_info)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, provider)
        print("✅ Medical providers inserted (15 records)")

        # Insert Exclusions
        exclusions_data = [
            ('EXC_001', 'Pre-existing Disease', 'Medical', 'Any condition diagnosed within 48 months prior', 'ALL',
             'HIGH'),
            ('EXC_002', 'War and War-like Operations', 'General', 'War, invasion, civil war, rebellion', 'ALL', 'HIGH'),
            ('EXC_003', 'Adventure Sports', 'Activity', 'Skydiving, bungee jumping, mountaineering',
             'BASE_001,BASE_003', 'HIGH'),
            ('EXC_004', 'Pregnancy and Childbirth', 'Medical', 'Pregnancy costs in travel insurance',
             'BASE_001,OPT_001', 'HIGH'),
            ('EXC_005', 'Intoxication', 'Behavioral', 'Under influence of alcohol or drugs', 'ALL', 'HIGH'),
            ('EXC_006', 'Cosmetic Treatment', 'Medical', 'Cosmetic surgery unless medically required',
             'BASE_001,OPT_001', 'MEDIUM'),
            ('EXC_007', 'Terrorism', 'Security', 'Acts of terrorism except specific covers', 'ALL', 'HIGH'),
            ('EXC_008', 'Air Ambulance Distance Limit', 'Geographic', 'Proportionate payment over 150km', 'EDL_001',
             'MEDIUM'),
            ('EXC_009', 'Infertility Treatment', 'Medical', 'Not covered under maternity policy',
             'EDL_002,EDL_003,EDL_004', 'HIGH'),
            ('EXC_010', 'Criminal Activities', 'Legal', 'Injuries during criminal activities', 'ALL', 'HIGH'),
            ('EXC_011', 'Nuclear Risks', 'Environmental', 'Ionizing radiation or contamination', 'ALL', 'HIGH'),
            ('EXC_012', 'Congenital Diseases', 'Medical', 'Congenital external diseases and defects', 'ALL', 'HIGH'),
            ('EXC_013', 'Mental Health Disorders', 'Medical', 'Psychiatric illnesses and mental disorders',
             'BASE_001,OPT_001', 'HIGH'),
            ('EXC_014', 'Experimental Treatments', 'Medical', 'Treatments not based on established practice', 'ALL',
             'HIGH'),
            ('EXC_015', 'Hazardous Occupations', 'Occupational', 'Injuries during hazardous work',
             'BASE_003,BASE_004,BASE_005', 'HIGH')
        ]

        for exclusion in exclusions_data:
            self.cursor.execute("""
                            INSERT INTO EXCLUSIONS 
                            (exclusion_id, exclusion_name, exclusion_type, description, applicable_coverage, severity)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, exclusion)
        print("✅ Exclusions inserted (15 records)")

        # Insert Policy Rules
        rules_data = [
            ('RULE_001', 'Age Eligibility', 'ELIGIBILITY', 'BASE_001', 'age >= 0.25 AND age <= 90', 'ELIGIBLE', 1,
             True),
            ('RULE_002', 'Trip Duration Limit', 'DURATION', 'ALL', 'trip_duration <= 365', 'ELIGIBLE', 1, True),
            ('RULE_003', 'India Territory Only', 'GEOGRAPHIC', 'ALL', 'incident_location IN India', 'ELIGIBLE', 1,
             True),
            ('RULE_004', 'Hospitalization Minimum', 'DURATION', 'BASE_001', 'hospitalization_hours >= 24', 'ELIGIBLE',
             2, True),
            ('RULE_005', 'Air Ambulance Distance', 'GEOGRAPHIC', 'EDL_001', 'distance_km <= 150', 'ELIGIBLE', 1, True),
            ('RULE_006', 'Well Mother Age', 'ELIGIBILITY', 'EDL_002,EDL_003,EDL_004', 'age >= 18 AND age <= 50',
             'ELIGIBLE', 1, True),
            ('RULE_007', 'Newborn Age Limit', 'ELIGIBILITY', 'EDL_005', 'age_days <= 30', 'ELIGIBLE', 1, True),
            ('RULE_008', 'Policy Validity', 'ADMINISTRATIVE', 'ALL', 'incident_date BETWEEN start_date AND end_date',
             'ELIGIBLE', 1, True),
            ('RULE_009', 'Sum Insured Limit', 'FINANCIAL', 'ALL', 'claim_amount <= sum_insured', 'ELIGIBLE', 1, True),
            ('RULE_010', 'Claim Notification Time', 'ADMINISTRATIVE', 'ALL', 'notification_days <= 30', 'ELIGIBLE', 1,
             True),
            ('RULE_011', 'Pre-existing Condition Check', 'MEDICAL', 'BASE_001',
             'has_pre_existing = True AND not_life_threatening = True', 'EXCLUDED', 1, True),
            ('RULE_012', 'Dental - Accidental Only', 'MEDICAL', 'OPT_005', 'dental_cause != "ACCIDENT"', 'EXCLUDED', 1,
             True),
            ('RULE_013', 'Baggage - Airways Only', 'TRANSPORT', 'OPT_011', 'transport_mode != "AIRWAYS"', 'EXCLUDED', 1,
             True),
            ('RULE_014', 'Medical Practitioner Validity', 'REGULATORY', 'ALL', 'medical_practitioner_licensed = True',
             'ELIGIBLE', 1, True),
            ('RULE_015', 'Treatment Delay Assessment', 'MEDICAL', 'BASE_001,OPT_001', 'treatment_can_be_delayed = True',
             'EXCLUDED', 2, True)
        ]

        for rule in rules_data:
            self.cursor.execute("""
                            INSERT INTO POLICY_RULES 
                            (rule_id, rule_name, rule_type, coverage_id, rule_condition, rule_result, priority, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, rule)
        print("✅ Policy rules inserted (15 records)")

        # Insert Pre-existing Conditions
        conditions_data = [
            ('COND_001', 'INS_005', 'Diabetes Type 2', '2020-03-15', 'Moderate', True, 'Under medication control'),
            ('COND_002', 'INS_012', 'Hypertension', '2019-08-20', 'Mild', True, 'Regular medication'),
            ('COND_003', 'INS_014', 'Asthma', '2018-12-10', 'Moderate', True, 'Inhaler treatment'),
            ('COND_004', 'INS_003', 'Heart Disease', '2021-01-25', 'Severe', True, 'Cardiac medication'),
            ('COND_005', 'INS_023', 'Arthritis', '2020-09-12', 'Moderate', True, 'Anti-inflammatory treatment'),
            ('COND_006', 'INS_008', 'Thyroid Disorder', '2020-06-18', 'Mild', True, 'Hormone replacement therapy'),
            ('COND_007', 'INS_019', 'High Cholesterol', '2019-11-30', 'Moderate', True, 'Statin medication'),
            ('COND_008', 'INS_015', 'Migraine', '2018-05-07', 'Mild', True, 'Preventive medication'),
            ('COND_009', 'INS_027', 'Sleep Apnea', '2021-03-22', 'Moderate', True, 'CPAP therapy'),
            ('COND_010', 'INS_011', 'Kidney Stones', '2019-07-14', 'Mild', True, 'Dietary management')
        ]

        for condition in conditions_data:
            self.cursor.execute("""
                            INSERT INTO PREEXISTING_CONDITIONS 
                            (condition_id, insured_id, condition_name, diagnosed_date, severity, is_disclosed, treatment_history)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, condition)
        print("✅ Pre-existing conditions inserted (10 records)")

        # Insert Claim Documents (sample for first 15 claims)
        claim_documents_data = [
            ('CLM_001', 'DOC_001', '2024-03-16', 'SUBMITTED'),
            ('CLM_001', 'DOC_006', '2024-03-16', 'SUBMITTED'),
            ('CLM_001', 'DOC_007', '2024-03-16', 'SUBMITTED'),
            ('CLM_001', 'DOC_014', '2024-03-16', 'SUBMITTED'),
            ('CLM_002', 'DOC_009', '2024-03-21', 'SUBMITTED'),
            ('CLM_002', 'DOC_010', '2024-03-22', 'SUBMITTED'),
            ('CLM_002', 'DOC_014', '2024-03-21', 'SUBMITTED'),
            ('CLM_003', 'DOC_006', '2024-03-26', 'SUBMITTED'),
            ('CLM_003', 'DOC_007', '2024-03-26', 'SUBMITTED'),
            ('CLM_004', 'DOC_012', '2024-04-02', 'INCOMPLETE'),
            ('CLM_004', 'DOC_014', '2024-04-02', 'SUBMITTED'),
            ('CLM_005', 'DOC_011', '2024-04-06', 'SUBMITTED'),
            ('CLM_005', 'DOC_008', '2024-04-06', 'SUBMITTED'),
            ('CLM_006', 'DOC_015', '2024-04-11', 'SUBMITTED'),
            ('CLM_006', 'DOC_016', '2024-04-11', 'SUBMITTED'),
            ('CLM_006', 'DOC_017', '2024-04-11', 'SUBMITTED'),
            ('CLM_007', 'DOC_018', '2024-04-16', 'SUBMITTED'),
            ('CLM_007', 'DOC_019', '2024-04-16', 'SUBMITTED'),
            ('CLM_008', 'DOC_020', '2024-04-21', 'SUBMITTED'),
            ('CLM_008', 'DOC_021', '2024-04-21', 'SUBMITTED'),
            ('CLM_009', 'DOC_018', '2024-04-26', 'SUBMITTED'),
            ('CLM_009', 'DOC_019', '2024-04-26', 'SUBMITTED'),
            ('CLM_010', 'DOC_018', '2024-05-02', 'SUBMITTED'),
            ('CLM_011', 'DOC_024', '2024-05-06', 'SUBMITTED'),
            ('CLM_013', 'DOC_013', '2024-05-16', 'SUBMITTED'),
            ('CLM_013', 'DOC_008', '2024-05-16', 'SUBMITTED'),
            ('CLM_015', 'DOC_023', '2024-05-26', 'SUBMITTED'),
            ('CLM_015', 'DOC_014', '2024-05-26', 'SUBMITTED')
        ]

        for claim_doc in claim_documents_data:
            self.cursor.execute("""
                            INSERT INTO CLAIM_DOCUMENTS 
                            (claim_id, document_id, submission_date, status)
                            VALUES (?, ?, ?, ?)
                        """, claim_doc)
        print("✅ Claim documents inserted (28 records)")

        # Insert Claim Assessments
        assessments_data = [
            ('ASMT_001', 'CLM_001', 'ASR_001', '2024-03-18', 'APPROVED', 25000.00, 25000.00,
             'Claim meets all policy criteria'),
            ('ASMT_002', 'CLM_002', 'ASR_002', '2024-03-23', 'APPROVED', 500000.00, 500000.00,
             'Valid accidental death claim'),
            ('ASMT_003', 'CLM_003', 'ASR_001', '2024-03-28', 'UNDER_REVIEW', 15000.00, 0.00,
             'Reviewing medical necessity'),
            ('ASMT_004', 'CLM_004', 'ASR_003', '2024-04-05', 'REJECTED', 8000.00, 0.00, 'Insufficient documentation'),
            ('ASMT_005', 'CLM_005', 'ASR_002', '2024-04-08', 'APPROVED', 300000.00, 300000.00,
             'Permanent disability confirmed'),
            ('ASMT_006', 'CLM_006', 'ASR_004', '2024-04-13', 'UNDER_REVIEW', 45000.00, 0.00,
             'Verifying distance and necessity'),
            ('ASMT_007', 'CLM_007', 'ASR_005', '2024-04-18', 'APPROVED', 12000.00, 12000.00, 'Prenatal care approved'),
            ('ASMT_008', 'CLM_008', 'ASR_005', '2024-04-23', 'APPROVED', 8000.00, 8000.00, 'Newborn care approved'),
            ('ASMT_009', 'CLM_009', 'ASR_005', '2024-04-28', 'APPROVED', 18000.00, 18000.00, 'Maternity care approved'),
            ('ASMT_010', 'CLM_011', 'ASR_001', '2024-05-08', 'APPROVED', 35000.00, 35000.00,
             'Medical evacuation justified'),
            ('ASMT_011', 'CLM_012', 'ASR_003', '2024-05-13', 'REJECTED', 20000.00, 0.00,
             'Condition not life-threatening'),
            ('ASMT_012', 'CLM_013', 'ASR_001', '2024-05-18', 'APPROVED', 5000.00, 5000.00, 'Emergency dental valid'),
            ('ASMT_013', 'CLM_015', 'ASR_001', '2024-05-28', 'APPROVED', 3000.00, 3000.00, 'Flight delay approved'),
            ('ASMT_014', 'CLM_017', 'ASR_005', '2024-06-08', 'APPROVED', 9500.00, 9500.00,
             'Prenatal diagnostics approved'),
            ('ASMT_015', 'CLM_018', 'ASR_005', '2024-06-13', 'APPROVED', 6500.00, 6500.00,
             'Newborn immunizations approved'),
            ('ASMT_016', 'CLM_020', 'ASR_005', '2024-06-23', 'APPROVED', 25000.00, 25000.00,
             'Complete maternity care approved'),
            ('ASMT_017', 'CLM_022', 'ASR_002', '2024-07-03', 'APPROVED', 75000.00, 75000.00,
             'Partial disability compensation approved'),
            ('ASMT_018', 'CLM_023', 'ASR_001', '2024-07-08', 'APPROVED', 4000.00, 4000.00, 'Daily allowance approved'),
            ('ASMT_019', 'CLM_025', 'ASR_003', '2024-07-18', 'APPROVED', 12000.00, 12000.00, 'Baggage loss approved'),
            ('ASMT_020', 'CLM_026', 'ASR_005', '2024-07-23', 'APPROVED', 16500.00, 16500.00, 'Maternity care approved')
        ]

        for assessment in assessments_data:
            self.cursor.execute("""
                        INSERT INTO CLAIM_ASSESSMENTS 
                        (assessment_id, claim_id, assessor_id, assessment_date, status, recommended_amount, approved_amount, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, assessment)
        print("✅ Claim assessments inserted (20 records)")

        # Insert Claim History
        history_data = [
            ('HIST_001', 'CLM_001', 'SUBMITTED', 'UNDER_REVIEW', 'ASR_001', '2024-03-16 10:00:00',
             'Initial review started'),
            ('HIST_002', 'CLM_001', 'UNDER_REVIEW', 'APPROVED', 'ASR_001', '2024-03-18 14:30:00',
             'All documents verified'),
            ('HIST_003', 'CLM_002', 'SUBMITTED', 'UNDER_REVIEW', 'ASR_002', '2024-03-21 09:15:00',
             'Death claim investigation'),
            ('HIST_004', 'CLM_002', 'UNDER_REVIEW', 'APPROVED', 'ASR_002', '2024-03-23 16:45:00',
             'Investigation complete'),
            ('HIST_005', 'CLM_003', 'SUBMITTED', 'UNDER_REVIEW', 'ASR_001', '2024-03-26 11:20:00',
             'Medical review required'),
            ('HIST_006', 'CLM_004', 'SUBMITTED', 'UNDER_REVIEW', 'ASR_003', '2024-04-02 08:30:00',
             'Document verification'),
            ('HIST_007', 'CLM_004', 'UNDER_REVIEW', 'REJECTED', 'ASR_003', '2024-04-05 15:00:00',
             'Insufficient documentation'),
            ('HIST_008', 'CLM_005', 'SUBMITTED', 'APPROVED', 'ASR_002', '2024-04-08 12:00:00', 'Disability confirmed'),
            ('HIST_009', 'CLM_006', 'SUBMITTED', 'UNDER_REVIEW', 'ASR_004', '2024-04-11 09:45:00',
             'Distance verification needed'),
            ('HIST_010', 'CLM_007', 'SUBMITTED', 'APPROVED', 'ASR_005', '2024-04-18 13:30:00',
             'Prenatal care approved'),
            ('HIST_011', 'CLM_008', 'SUBMITTED', 'APPROVED', 'ASR_005', '2024-04-23 10:15:00', 'Newborn care approved'),
            ('HIST_012', 'CLM_009', 'SUBMITTED', 'APPROVED', 'ASR_005', '2024-04-28 14:00:00', 'Maternity approved'),
            ('HIST_013', 'CLM_011', 'SUBMITTED', 'APPROVED', 'ASR_001', '2024-05-08 11:30:00', 'Evacuation justified'),
            ('HIST_014', 'CLM_012', 'SUBMITTED', 'REJECTED', 'ASR_003', '2024-05-13 16:15:00', 'Not life-threatening'),
            ('HIST_015', 'CLM_013', 'SUBMITTED', 'APPROVED', 'ASR_001', '2024-05-18 12:45:00', 'Emergency dental valid')
        ]

        for history in history_data:
            self.cursor.execute("""
                        INSERT INTO CLAIM_HISTORY 
                        (history_id, claim_id, status_from, status_to, changed_by, change_date, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, history)
        print("✅ Claim history inserted (15 records)")

        # Commit all transactions
        self.connection.commit()
        print("\n🎉 Database setup completed successfully!")
        print(f"Database '{self.db_name}' created with comprehensive sample data.")

    def get_claims_summary(self):
        """Get a summary of claims by status"""
        query = """
                    SELECT status, COUNT(*) as count, SUM(claim_amount) as total_claimed, 
                           SUM(approved_amount) as total_approved
                    FROM CLAIMS 
                    GROUP BY status
                    ORDER BY count DESC
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_top_coverage_claims(self, limit=5):
        """Get top coverage types by claim count"""
        query = """
                    SELECT ct.coverage_name, COUNT(c.claim_id) as claim_count, 
                           SUM(c.claim_amount) as total_claimed,
                           SUM(c.approved_amount) as total_approved
                    FROM CLAIMS c
                    JOIN COVERAGE_TYPES ct ON c.coverage_id = ct.coverage_id
                    GROUP BY ct.coverage_id, ct.coverage_name
                    ORDER BY claim_count DESC
                    LIMIT ?
                """
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()

    def get_claims_by_policy(self, policy_id):
        """Get all claims for a specific policy"""
        query = """
                    SELECT c.claim_id, ip.name, ct.coverage_name, c.status, 
                           c.claim_date, c.claim_amount, c.approved_amount, c.description
                    FROM CLAIMS c
                    JOIN INSURED_PERSONS ip ON c.insured_id = ip.insured_id
                    JOIN COVERAGE_TYPES ct ON c.coverage_id = ct.coverage_id
                    WHERE c.policy_id = ?
                    ORDER BY c.claim_date DESC
                """
        self.cursor.execute(query, (policy_id,))
        return self.cursor.fetchall()

    def get_insured_with_preexisting_conditions(self):
        """Get insured persons with pre-existing conditions"""
        query = """
                    SELECT ip.name, ip.city, ip.state, pc.condition_name, 
                           pc.severity, pc.diagnosed_date, pc.is_disclosed
                    FROM INSURED_PERSONS ip
                    JOIN PREEXISTING_CONDITIONS pc ON ip.insured_id = pc.insured_id
                    ORDER BY ip.name
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_claims_requiring_documents(self):
        """Get claims with pending document requirements"""
        query = """
                    SELECT c.claim_id, ip.name, ct.coverage_name, c.status,
                           COUNT(cd.document_id) as submitted_docs,
                           GROUP_CONCAT(rd.document_name) as pending_docs
                    FROM CLAIMS c
                    JOIN INSURED_PERSONS ip ON c.insured_id = ip.insured_id
                    JOIN COVERAGE_TYPES ct ON c.coverage_id = ct.coverage_id
                    LEFT JOIN CLAIM_DOCUMENTS cd ON c.claim_id = cd.claim_id AND cd.status = 'SUBMITTED'
                    LEFT JOIN REQUIRED_DOCUMENTS rd ON (ct.coverage_id = rd.coverage_id OR rd.coverage_id = 'ALL')
                    WHERE c.status IN ('SUBMITTED', 'UNDER_REVIEW')
                    GROUP BY c.claim_id, ip.name, ct.coverage_name, c.status
                    ORDER BY c.claim_date
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        """Close the database connection"""
        self.connection.close()
        print("Database connection closed.")

    def run_sample_queries(self):
        """Run sample queries to demonstrate the database"""
        print("\n" + "=" * 60)
        print("SAMPLE DATABASE QUERIES")
        print("=" * 60)

        # Claims Summary
        print("\n1. CLAIMS SUMMARY BY STATUS:")
        print("-" * 40)
        claims_summary = self.get_claims_summary()
        for row in claims_summary:
            print(
                f"Status: {row[0]:<15} Count: {row[1]:<3} Total Claimed: ₹{row[2]:,.2f} Total Approved: ₹{row[3]:,.2f}")

        # Top Coverage Claims
        print("\n2. TOP 5 COVERAGE TYPES BY CLAIMS:")
        print("-" * 40)
        top_coverage = self.get_top_coverage_claims()
        for row in top_coverage:
            print(f"Coverage: {row[0]:<40} Claims: {row[1]:<3} Claimed: ₹{row[2]:,.2f}")

        # Sample Policy Claims
        print(f"\n3. CLAIMS FOR POLICY 'CHOTGDP23004V012223':")
        print("-" * 40)
        policy_claims = self.get_claims_by_policy('CHOTGDP23004V012223')
        for row in policy_claims[:5]:  # Show first 5
            print(f"Claim: {row[0]} | {row[1]} | {row[2]:<30} | {row[3]:<12} | ₹{row[5]:,.2f}")

        # Pre-existing Conditions
        print(f"\n4. INSURED PERSONS WITH PRE-EXISTING CONDITIONS:")
        print("-" * 40)
        preexisting = self.get_insured_with_preexisting_conditions()
        for row in preexisting[:5]:  # Show first 5
            print(f"{row[0]:<20} | {row[3]:<20} | {row[4]:<10} | Disclosed: {row[6]}")

        print("\n" + "=" * 60)

    # Main execution
    if __name__ == "__main__":
        # Create database instance
        db = InsuranceClaimsDatabase()

        try:
            # Create tables and insert data
            db.create_tables()
            db.insert_sample_data()

            # Run sample queries
            db.run_sample_queries()

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            # Close connection
            db.close_connection()