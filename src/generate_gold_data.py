import os
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")
TIMESTAMP = "2026-08-25T23:00:00Z"


def make_field(val, evidence_list=None, status="verified", conf=1.0):
    if status == "not_found" or val is None:
        return {
            "value": None,
            "evidence": [],
            "confidence": 1.0,
            "verification_status": "not_found"
        }
    
    ev_items = []
    if evidence_list:
        for item in evidence_list:
            if isinstance(item, str):
                ev_items.append({
                    "text": item,
                    "locator": {
                        "page": None,
                        "section": None,
                        "document_location": None,
                        "url": None,
                        "source_reference": None
                    }
                })
            elif isinstance(item, dict):
                ev_items.append(item)
    else:
        ev_items.append({
            "text": str(val) if isinstance(val, str) else json.dumps(val),
            "locator": {"page": None, "section": None, "document_location": None, "url": None, "source_reference": None}
        })
        
    return {
        "value": val,
        "evidence": ev_items,
        "confidence": conf,
        "verification_status": status
    }


def create_gold_records():
    os.makedirs(GOLD_DIR, exist_ok=True)
    
    # ----------------------------------------------------
    # GOV-E-01
    # ----------------------------------------------------
    gov_e01 = {
        "document_metadata": {
            "document_id": "GOV-E-01",
            "source_type": "HTML",
            "source_identifier": "https://myscheme.gov.in/schemes/pm-pms-sc",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "Post-Matric Scholarship for SC Students (PM-PMS-SC)",
            [{"text": "Post-Matric Scholarship for SC Students", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Header"}}]
        ),
        "scheme_type": make_field(
            "Centrally Sponsored Scheme / Post-Matric Scholarship",
            [{"text": "Centrally Sponsored Scheme for SC Students", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Details"}}]
        ),
        "implementing_authority": make_field(
            "Ministry of Social Justice and Empowerment, Government of India",
            [{"text": "Ministry of Social Justice and Empowerment", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Details"}}]
        ),
        "target_beneficiaries": make_field(
            "Students belonging to Scheduled Castes (SC) pursuing post-matriculation courses",
            [{"text": "Students belonging to Scheduled Castes studying at post-matriculation or post-secondary stage", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "education_level": make_field(
            "Post-Matriculation / Post-Secondary (Class 11 to Post-Graduation / Ph.D.)",
            [{"text": "Post-Matriculation or Post-Secondary stage in recognized institutions", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(None, status="not_found"),
        "income_criteria": make_field(
            "Annual family income from all sources must not exceed Rs. 2,50,000 per annum",
            [{"text": "Total annual family income of parents/guardians from all sources does not exceed Rs. 2.50 Lakh", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "academic_criteria": make_field(
            "Must have passed Class 10 / Matriculation or equivalent examination",
            [{"text": "Must have passed Matriculation or Higher Secondary examination", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "category_criteria": make_field(
            "Scheduled Caste (SC)",
            [{"text": "Belonging to Scheduled Castes community", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(
            "Indian Citizen domiciled in the respective State / UT",
            [{"text": "Resident of the state/UT to which the applicant belongs", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Eligibility"}}]
        ),
        "benefit_type": make_field(
            "Compulsory non-refundable fee support and academic maintenance allowance",
            [{"text": "Enrollment/tuition fee reimbursement and monthly academic maintenance allowance", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Benefits"}}]
        ),
        "benefit_amount": make_field(
            "Full compulsory non-refundable tuition fee coverage plus annual maintenance allowance ranging from Rs. 2,500 to Rs. 13,500 per annum depending on course group",
            [{"text": "Full fee reimbursement and maintenance allowance up to Rs. 13,500 per annum for hostellers and day scholars", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Benefits"}}]
        ),
        "application_method": make_field(
            "Online application through National Scholarship Portal (NSP) or State Scholarship Portals",
            [{"text": "Apply online through National Scholarship Portal or respective State Portal", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Application Process"}}]
        ),
        "application_url": make_field(
            "https://scholarships.gov.in",
            [{"text": "National Scholarship Portal https://scholarships.gov.in", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Application Process"}}]
        ),
        "required_documents": make_field(
            ["Scheduled Caste Certificate", "Family Income Certificate", "Class 10 / Matriculation Marksheet", "Aadhaar Card linked Bank Account details", "Current Academic Year Fee Receipt"],
            [{"text": "Caste Certificate, Income Certificate, Academic Marksheet, Aadhaar Details, Fee Receipt", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Documents Required"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active / Open for Application", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-E-02
    # ----------------------------------------------------
    gov_e02 = {
        "document_metadata": {
            "document_id": "GOV-E-02",
            "source_type": "HTML",
            "source_identifier": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "CSIR Junior Research Fellowship (CSIR JRF)",
            [{"text": "CSIR Junior Research Fellowship (JRF)", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Title"}}]
        ),
        "scheme_type": make_field(
            "Research Fellowship Scheme",
            [{"text": "Research Fellowship for Ph.D. studies", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Overview"}}]
        ),
        "implementing_authority": make_field(
            "Council of Scientific and Industrial Research (CSIR) - Human Resource Development Group (HRDG)",
            [{"text": "Council of Scientific and Industrial Research - Human Resource Development Group", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Header"}}]
        ),
        "target_beneficiaries": make_field(
            "M.Sc. or equivalent degree holders in science and technology qualifying CSIR-UGC NET examination",
            [{"text": "Indian nationals qualifying the CSIR-UGC NET exam holding M.Sc or equivalent degree", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Eligibility"}}]
        ),
        "education_level": make_field(
            "Post-Graduate Degree (M.Sc., BS-4 years, BE/B.Tech, B.Pharm, MBBS, Integrated BS-MS)",
            [{"text": "M.Sc. or equivalent degree, BS-4 years, BE/B.Tech, B.Pharm, MBBS", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(
            "Maximum age limit 28 years (relaxable up to 5 years for SC/ST/Third gender/Persons with Disabilities/female applicants and 3 years for OBC non-creamy layer)",
            [{"text": "Maximum 28 years as on date of exam. Relaxation up to 5 years for SC/ST/PwD/Women and 3 years for OBC", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Age Limit"}}]
        ),
        "income_criteria": make_field(None, status="not_found"),
        "academic_criteria": make_field(
            "Minimum 55% marks for General/General-EWS/OBC candidates and 50% for SC/ST/Third gender/PwD candidates in qualifying degree",
            [{"text": "55% marks for General/OBC and 50% for SC/ST/PwD candidates in M.Sc or equivalent", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Educational Qualification"}}]
        ),
        "category_criteria": make_field(
            "General, General-EWS, OBC (NCL), SC, ST, Third gender, PwD (Age and marks relaxation applicable)",
            [{"text": "Relaxations provided for SC/ST/OBC/PwD/Third Gender/Women candidates", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(
            "Indian National",
            [{"text": "Candidate must be a citizen of India", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Eligibility"}}]
        ),
        "benefit_type": make_field(
            "Monthly Research Stipend and Annual Contingency Grant",
            [{"text": "Monthly stipend plus contingency grant", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Stipend and Tenure"}}]
        ),
        "benefit_amount": make_field(
            "Stipend of Rs. 31,000 per month for initial 2 years (JRF), upgradable to Rs. 35,000 per month as SRF for remaining 3 years, plus annual contingency grant of Rs. 20,000",
            [{"text": "Rs. 31,000/- p.m. for 1st & 2nd year (JRF) and Rs. 35,000/- p.m. for 3rd and subsequent year (SRF) plus annual contingency grant of Rs. 20,000/-", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Stipend and Tenure"}}]
        ),
        "application_method": make_field(
            "Online application through CSIR-UGC NET portal and CSIR HRDG online system",
            [{"text": "Apply online through NTA CSIR-NET official web portal", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "How to Apply"}}]
        ),
        "application_url": make_field(
            "https://csirhrdg.res.in",
            [{"text": "https://csirhrdg.res.in", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Header"}}]
        ),
        "required_documents": make_field(
            ["CSIR-UGC NET JRF Rank Certificate", "Post-Graduation Degree / Provisional Certificate", "Category / Caste Certificate", "Age Proof / Class 10 Certificate", "Joining Report from Research Institution"],
            [{"text": "JRF Certificate, Qualifying Degree, Category Certificate, Age Proof, Joining Report", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Documents Required"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active Guidelines", "locator": {"url": "https://csirhrdg.res.in/Home/Index/1/Default/3384/60", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-E-03
    # ----------------------------------------------------
    gov_e03 = {
        "document_metadata": {
            "document_id": "GOV-E-03",
            "source_type": "HTML",
            "source_identifier": "https://www.myscheme.gov.in/schemes/pssgtd",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "Pragati Scholarship Scheme for Girl Students (Technical Degree)",
            [{"text": "Pragati Scholarship Scheme for Girl Students (Technical Degree)", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Header"}}]
        ),
        "scheme_type": make_field(
            "Central Scholarship Scheme for Girl Students",
            [{"text": "AICTE Scheme for empowering girl students in technical education", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Details"}}]
        ),
        "implementing_authority": make_field(
            "All India Council for Technical Education (AICTE), Ministry of Education, Government of India",
            [{"text": "All India Council for Technical Education (AICTE)", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Details"}}]
        ),
        "target_beneficiaries": make_field(
            "Female students admitted to 1st year of Technical Degree course (or 2nd year lateral entry) in AICTE approved institutions",
            [{"text": "Girl students admitted to first year of Degree level course OR second year degree level course through lateral entry in AICTE approved institution", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "education_level": make_field(
            "1st Year Technical Degree or 2nd Year Lateral Entry Degree (B.E. / B.Tech)",
            [{"text": "Technical Degree course (Degree Level) in AICTE approved colleges", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(None, status="not_found"),
        "income_criteria": make_field(
            "Total annual family income must not exceed Rs. 8.00 Lakh per annum",
            [{"text": "Family income from all sources should not be more than Rs. 8 Lakh per annum", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "academic_criteria": make_field(
            "Admitted to AICTE approved technical degree program on the basis of merit",
            [{"text": "Admitted to degree course through centralized admission process of state/central government", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "category_criteria": make_field(
            "Female Students (Reservation for SC/ST/OBC as per Central Government norms)",
            [{"text": "Girl students (Maximum 2 girls per family eligible)", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(
            "Indian National",
            [{"text": "Indian Citizen", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Eligibility"}}]
        ),
        "benefit_type": make_field(
            "Annual lump sum scholarship financial support",
            [{"text": "Financial assistance of Rs. 50,000 per annum", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Benefits"}}]
        ),
        "benefit_amount": make_field(
            "Rs. 50,000 per annum for every year of study towards college fee, computer, books, stationery, equipment, and software purchase",
            [{"text": "Rs. 50,000/- per annum for every year of study as specific lump sum amount towards college fee, books, computer, software, equipment etc.", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Benefits"}}]
        ),
        "application_method": make_field(
            "Online application through National Scholarship Portal (NSP)",
            [{"text": "Apply online through National Scholarship Portal (NSP)", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Application Process"}}]
        ),
        "application_url": make_field(
            "https://scholarships.gov.in",
            [{"text": "https://scholarships.gov.in", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Application Process"}}]
        ),
        "required_documents": make_field(
            ["Class 10 and Class 12 Marksheets", "Family Income Certificate", "Admission Letter to AICTE approved course", "Bank Account Details (Aadhaar Seeded)", "Parent Declaration for Girl Child"],
            [{"text": "Class 10 & 12 Marksheets, Income Certificate, Admission Letter, Aadhaar Seeded Bank Account, Parent Declaration", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Documents Required"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active / Open", "locator": {"url": "https://www.myscheme.gov.in/schemes/pssgtd", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-E-04
    # ----------------------------------------------------
    gov_e04 = {
        "document_metadata": {
            "document_id": "GOV-E-04",
            "source_type": "HTML",
            "source_identifier": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY)",
            [{"text": "Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY)", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Header"}}]
        ),
        "scheme_type": make_field(
            "Centrally Sponsored Umbrella Welfare & Infrastructure Scheme",
            [{"text": "Merged umbrella scheme framing Adarsh Gram, Income Generation, and Hostel Construction", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Overview"}}]
        ),
        "implementing_authority": make_field(
            "Ministry of Social Justice and Empowerment, Government of India",
            [{"text": "Department of Social Justice and Empowerment, Ministry of Social Justice & Empowerment", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Header"}}]
        ),
        "target_beneficiaries": make_field(
            "Scheduled Caste (SC) persons, families, and SC-dominated villages",
            [{"text": "Persons and households belonging to Scheduled Castes and SC majority villages", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Target Beneficiaries"}}]
        ),
        "education_level": make_field(None, status="not_found"),
        "income_criteria": make_field(
            "Persons / families belonging to SC community with annual income up to Rs. 2.50 Lakh (for income generating project subsidy)",
            [{"text": "Annual family income threshold up to Rs. 2.50 Lakh for skill development and income generation components", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(None, status="not_found"),
        "academic_criteria": make_field(None, status="not_found"),
        "category_criteria": make_field(
            "Scheduled Caste (SC)",
            [{"text": "Scheduled Castes (SC)", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(
            "India (SC dominant villages and districts)",
            [{"text": "SC dominant villages across Indian States/UTs", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Eligibility"}}]
        ),
        "benefit_type": make_field(
            "Grant-in-Aid for Adarsh Gram village development, Income Generating Project subsidies, and Hostel infrastructure construction grant",
            [{"text": "Infrastructure grant for Adarsh Gram, financial assistance for income generation, and hostel construction support", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Components & Benefits"}}]
        ),
        "benefit_amount": make_field(
            "Adarsh Gram: Rs. 21.00 Lakh per village; Income Generation: Financial assistance subsidy up to Rs. 50,000 or 50% of project cost per beneficiary; Hostels: Construction grant up to Rs. 3.00 Lakh per seat for boys hostel and Rs. 3.50 Lakh per seat for girls hostel",
            [{"text": "Adarsh Gram Rs. 21 Lakh per village; Income generation up to Rs. 50,000 per beneficiary; Hostels up to Rs. 3.50 Lakh per seat", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Financial Outlay"}}]
        ),
        "application_method": make_field(
            "Implementation through State Governments, UT Administrations, and PM-AJAY portal",
            [{"text": "Through State Governments/UTs and online portal", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Implementation"}}]
        ),
        "application_url": make_field(
            "https://dosje.gov.in",
            [{"text": "https://dosje.gov.in", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Header"}}]
        ),
        "required_documents": make_field(
            ["SC Certificate", "Income Certificate", "Income Generation Project Proposal", "Aadhaar Card", "Bank Account Details"],
            [{"text": "Caste certificate, Income proof, Project Proposal, Aadhaar Card, Bank details", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Documents"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active Scheme", "locator": {"url": "https://www.dosje.gov.in/organisation/pradhan-mantri-anusuchit-jaati-abhyuday-yojnapm-ajay/", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-M-01
    # ----------------------------------------------------
    gov_m01 = {
        "document_metadata": {
            "document_id": "GOV-M-01",
            "source_type": "HTML",
            "source_identifier": "https://fellowship.tribal.gov.in/",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "National Fellowship for Higher Education of ST Students (NFST)",
            [{"text": "National Fellowship for Higher Education of ST Students", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Header"}}]
        ),
        "scheme_type": make_field(
            "Central Sector Research Fellowship Scheme",
            [{"text": "Central Sector Scheme for ST students pursuing M.Phil and Ph.D.", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Scheme Scope"}}]
        ),
        "implementing_authority": make_field(
            "Ministry of Tribal Affairs, Government of India",
            [{"text": "Ministry of Tribal Affairs, Government of India", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Header"}}]
        ),
        "target_beneficiaries": make_field(
            "ST Students pursuing regular M.Phil. and Ph.D. courses in Indian Universities / Institutions",
            [{"text": "ST candidates who have secured admission in regular M.Phil / Ph.D. courses", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Eligibility"}}]
        ),
        "education_level": make_field(
            "Post-Graduate enrolled in regular M.Phil. or Ph.D. program",
            [{"text": "Enrolled in regular M.Phil or Ph.D course in recognized university", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(None, status="not_found"),
        "income_criteria": make_field(None, status="not_found"),
        "academic_criteria": make_field(
            "Must have qualified Post-Graduation examination and obtained admission to regular M.Phil / Ph.D",
            [{"text": "Post-Graduation degree and admission in regular M.Phil/Ph.D", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Eligibility"}}]
        ),
        "category_criteria": make_field(
            "Scheduled Tribes (ST)",
            [{"text": "Scheduled Tribes (ST)", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(
            "Indian National belonging to ST community",
            [{"text": "ST candidates of Indian nationality", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Eligibility"}}]
        ),
        "benefit_type": make_field(
            "Monthly Fellowship Stipend, Contingency Grant, and House Rent Allowance (HRA)",
            [{"text": "Fellowship stipend, contingency allowance, and HRA", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Financial Assistance"}}]
        ),
        "benefit_amount": make_field(
            ["Stipend: Rs. 31,000 per month for JRF (first 2 years); Rs. 35,000 per month for SRF (remaining tenure)", "Contingency Grant: Humanities & Social Sciences: Rs. 10,000 per annum (JRF) / Rs. 20,500 per annum (SRF); Science, Engineering & Technology: Rs. 12,000 per annum (JRF) / Rs. 25,000 per annum (SRF)", "Escort / Reader Allowance: Rs. 2,000 per month for physically handicapped / visually impaired fellows", "HRA as per Central Government rates"],
            [{"text": "JRF Rs. 31,000/- p.m., SRF Rs. 35,000/- p.m., Contingency up to Rs. 25,000/- p.a., Escort allowance Rs. 2,000/- p.m.", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Financial Assistance"}}]
        ),
        "application_method": make_field(
            "Online application through MoTA Fellowship Portal",
            [{"text": "Apply online through Ministry of Tribal Affairs Fellowship portal", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Application Portal"}}]
        ),
        "application_url": make_field(
            "https://fellowship.tribal.gov.in",
            [{"text": "https://fellowship.tribal.gov.in", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Header"}}]
        ),
        "required_documents": make_field(
            ["ST Category Certificate", "Post-Graduation Marksheet and Degree", "M.Phil / Ph.D Admission Offer Letter and Registration Certificate", "Aadhaar Card", "Bank Account Details", "Disability Certificate (if claiming Escort Allowance)"],
            [{"text": "ST Certificate, PG Marksheet/Degree, Ph.D/M.Phil Admission letter, Aadhaar Card, Bank details", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Documents"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active Portal", "locator": {"url": "https://fellowship.tribal.gov.in/", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-M-02
    # ----------------------------------------------------
    gov_m02 = {
        "document_metadata": {
            "document_id": "GOV-M-02",
            "source_type": "HTML",
            "source_identifier": "https://www.myscheme.gov.in/schemes/pmy-tcc",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "PM-YASASVI: Top Class College Education for OBC EBC and DNT Students",
            [{"text": "PM-YASASVI Top Class College Education for OBC, EBC and DNT Students", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Header"}}]
        ),
        "scheme_type": make_field(
            "Central Sector Scholarship Scheme",
            [{"text": "Top Class College Education Scholarship Scheme", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Details"}}]
        ),
        "implementing_authority": make_field(
            "Ministry of Social Justice and Empowerment, Government of India",
            [{"text": "Department of Social Justice & Empowerment, MoSJE", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Details"}}]
        ),
        "target_beneficiaries": make_field(
            "OBC, EBC, and DNT students admitted to notified Top Class Higher Education Institutions",
            [{"text": "Students belonging to OBC, EBC and DNT categories studying in notified top class institutions", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Eligibility"}}]
        ),
        "education_level": make_field(
            "Full-time Degree / Diploma course in notified Top Class Educational Institutions",
            [{"text": "Full time degree/diploma course in notified top class institutions (IITs, NITs, IIMs, AIIMS, NLU, etc.)", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Eligibility"}}]
        ),
        "age_criteria": make_field(None, status="not_found"),
        "income_criteria": make_field(
            "Total annual family income from all sources must not exceed Rs. 2.50 Lakh per annum",
            [{"text": "Annual family income from all sources does not exceed Rs. 2.50 Lakh", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Eligibility"}}]
        ),
        "academic_criteria": make_field(
            "Admitted to notified top class institution as per full-time course admission norms",
            [{"text": "Admitted into notified top class institution", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Eligibility"}}]
        ),
        "category_criteria": make_field(
            ["Other Backward Classes (OBC)", "Economically Backward Classes (EBC)", "De-notified, Nomadic and Semi-Nomadic Tribes (DNT)", "30% slot reservation for female students"],
            [{"text": "OBC, EBC, and DNT categories with 30% slots reserved for girl students", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Eligibility"}}]
        ),
        "domicile_criteria": make_field(None, status="not_found"),
        "benefit_type": make_field(
            "4-Component Full Financial Assistance Package",
            [{"text": "4-component package covering tuition fee, living expenses, books allowance, and computer purchase", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Benefits"}}]
        ),
        "benefit_amount": make_field(
            ["Full tuition fee and non-refundable charges up to Rs. 2.00 Lakh per annum for private institutions (actual fee for government institutions)", "Living expenses of Rs. 3,000 per month (Rs. 36,000 per annum)", "Books and stationery allowance of Rs. 5,000 per annum", "One-time assistance of Rs. 45,000 for computer/laptop with accessories"],
            [{"text": "Tuition fee up to Rs. 2.00 Lakh/year, Living expenses Rs. 3,000/month, Books Rs. 5,000/year, Computer Rs. 45,000 one-time", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Benefits"}}]
        ),
        "application_method": make_field(
            "Online application through National Scholarship Portal (NSP)",
            [{"text": "Apply online through National Scholarship Portal", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Application Process"}}]
        ),
        "application_url": make_field(
            "https://scholarships.gov.in",
            [{"text": "https://scholarships.gov.in", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Application Process"}}]
        ),
        "required_documents": make_field(
            ["Caste / Category Certificate (OBC/EBC/DNT)", "Annual Family Income Certificate", "Class 10 and Class 12 Marksheets", "Institute Admission Letter and Fee Receipt", "Aadhaar Card", "Bank Account Details"],
            [{"text": "Category Certificate, Income Certificate, Academic Marksheets, Admission Letter, Aadhaar, Bank Details", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Documents Required"}}]
        ),
        "application_deadline": make_field(None, status="not_found"),
        "scheme_status": make_field(
            "Active",
            [{"text": "Active / Open", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc", "section": "Header"}}]
        )
    }

    # ----------------------------------------------------
    # GOV-M-03 (PDF with exact page locators!)
    # ----------------------------------------------------
    gov_m03 = {
        "document_metadata": {
            "document_id": "GOV-M-03",
            "source_type": "PDF",
            "source_identifier": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2023/10/20231005812894382.pdf",
            "extraction_timestamp": TIMESTAMP
        },
        "scheme_name": make_field(
            "National Bioenergy Programme - Biomass Programme (Phase-I)",
            [{"text": "Administrative approval for implementation of Biomass Programme under the Umbrella scheme of National Bioenergy Programme for duration of FY 2021-22 to 2025-26 (Phase-I)", "locator": {"page": 1, "section": "Subject"}}]
        ),
        "scheme_type": make_field(
            "Central Sector Umbrella Scheme / Financial Assistance Support Grant",
            [{"text": "implementation of the National Bioenergy Programme for a period of 01.04.2021 to 31.03.2026 with the outlay of Rs.858 crore under Phase-I", "locator": {"page": 1, "section": "Section 1"}}]
        ),
        "implementing_authority": make_field(
            "Ministry of New and Renewable Energy (Biomass Division), Government of India",
            [{"text": "Government of India Ministry of New and Renewable Energy (Biomass Division) Atal Akshay Urja Bhawan, Lodhi Road, New Delhi-110 003", "locator": {"page": 1, "section": "Header"}}]
        ),
        "target_beneficiaries": make_field(
            "Project Developers, Manufacturers, Industrial Units setting up Biomass Pellet/Briquette manufacturing plants or Biomass Cogeneration (non-bagasse) projects",
            [{"text": "Central Financial Assistance (CFA) under Biomass Programme for setting up of Biomass pellet/briquette manufacturing plants and Biomass cogeneration (non-bagasse) projects", "locator": {"page": 2, "section": "Section 3"}}]
        ),
        "education_level": make_field(None, status="not_found"),
        "income_criteria": make_field(None, status="not_found"),
        "age_criteria": make_field(None, status="not_found"),
        "academic_criteria": make_field(None, status="not_found"),
        "category_criteria": make_field(None, status="not_found"),
        "domicile_criteria": make_field(None, status="not_found"),
        "benefit_type": make_field(
            "Central Financial Assistance (CFA) Capital Support Grant",
            [{"text": "Central Financial Assistance (CFA) under Biomass Programme for setting up of Biomass pellet/briquette manufacturing plants and Biomass cogeneration (non-bagasse) projects is given at Table 1.", "locator": {"page": 2, "section": "Section 3"}}]
        ),
        "benefit_amount": make_field(
            ["Pellet Manufacturing Plants: Rs. 3.00 Lakh per MTPH capacity (Max CFA Rs. 45.00 Lakh per project)", "Briquette Manufacturing Plants: Rs. 1.50 Lakh per MTPH capacity (Max CFA Rs. 15.00 Lakh per project)", "Biomass (Non-bagasse) Cogeneration: Rs. 40.00 Lakh per MW for power / Rs. 4.00 Lakh per MTPH steam (Max CFA Rs. 5.00 Crore per project)"],
            [
                {"text": "Pellet manufacturing plants: Rs. 3.00 Lakh / MTPH of capacity (Max CFA Rs. 45.00 Lakh per project)", "locator": {"page": 2, "section": "Table 1"}},
                {"text": "Briquette manufacturing plants: Rs. 1.50 Lakh / MTPH of capacity (Max CFA Rs. 15.00 Lakh per project)", "locator": {"page": 3, "section": "Table 1"}},
                {"text": "Biomass (non-bagasse) Cogeneration: Rs. 40.00 Lakh / MW for power generation / Rs. 4.00 Lakh / MTPH for steam generation (Max CFA Rs. 5.00 Crore per project)", "locator": {"page": 3, "section": "Table 1"}}
            ]
        ),
        "application_method": make_field(
            "Online submission through BioURJA Portal",
            [{"text": "The proposal for availing CFA should be submitted through BioURJA Portal (www.biourja.mnre.gov.in) before commissioning of the plant", "locator": {"page": 4, "section": "Clause 4.1(i)"}}]
        ),
        "application_url": make_field(
            "www.biourja.mnre.gov.in",
            [{"text": "(www.biourja.mnre.gov.in)", "locator": {"page": 4, "section": "Clause 4.1(i)"}}]
        ),
        "required_documents": make_field(
            ["Forwarding letter from developer/Lead FI/Bank (Annexure-II)", "Copy of Detailed Project Report (DPR) / Feasibility Report (Annexure-III)", "Copy of loan sanction letter (if bank financed)", "Techno-economic Feasibility Report", "Latest high-resolution site photographs with timestamp", "Duly notarized undertaking on Rs. 500 stamp paper (Annexure-V)", "Performance Inspection Report (Annexure-VI)", "CA Certificate detailing total project cost and source of funds", "Consent to Operate from State Pollution Control Board", "EIA clearance (where applicable)", "Contract agreement for sale of briquettes/pellets for minimum 2 years", "SCADA / remote monitoring system details"],
            [
                {"text": "Part A: List of documents required for in-principle approval of proposals (Annexure-I Part A)", "locator": {"page": 11, "section": "Annexure-I Part A"}},
                {"text": "Part B: List of documents required for release of CFA (Annexure-I Part B)", "locator": {"page": 11, "section": "Annexure-I Part B"}}
            ]
        ),
        "application_deadline": make_field(
            "31.12.2025",
            [{"text": "The last date for submitting the applications under these guidelines shall be 31.12.2025.", "locator": {"page": 4, "section": "Clause 4.1(i)"}}]
        ),
        "scheme_status": make_field(
            "Sanctioned for implementation from 01.04.2021 to 31.03.2026 (Application submission deadline: 31.12.2025)",
            [{"text": "implementation of the National Bioenergy Programme for a period of 01.04.2021 to 31.03.2026", "locator": {"page": 1, "section": "Section 1"}}]
        )
    }

    records = {
        "GOV-E-01": gov_e01,
        "GOV-E-02": gov_e02,
        "GOV-E-03": gov_e03,
        "GOV-E-04": gov_e04,
        "GOV-M-01": gov_m01,
        "GOV-M-02": gov_m02,
        "GOV-M-03": gov_m03
    }

    for doc_id, data in records.items():
        out_path = os.path.join(GOLD_DIR, f"{doc_id}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Created gold standard record: {out_path}")


if __name__ == "__main__":
    create_gold_records()

