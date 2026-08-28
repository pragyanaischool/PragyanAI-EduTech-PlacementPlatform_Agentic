import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ----------------------------------------------------
# 1. DIRECTORY CONFIGURATION & INITIALIZATION
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Create .gitkeep
with open(os.path.join(DATA_DIR, ".gitkeep"), "w") as f:
    pass

random.seed(42)
np.random.seed(42)

TOTAL_STUDENTS = 1500

# ----------------------------------------------------
# 2. DEPARTMENT TAXONOMIES & SKILL POOLS
# ----------------------------------------------------
DEPTS = {
    "CSE": {
        "weight": 0.22,
        "skills": ["Python", "Java", "C++", "FastAPI", "React", "Docker", "Kubernetes", "SQL", "Redis", "Kafka", "Data Structures", "System Design", "Go", "GraphQL", "gRPC"]
    },
    "AIML": {
        "weight": 0.16,
        "skills": ["Python", "PyTorch", "TensorFlow", "LangChain", "LangGraph", "FAISS", "Scikit-Learn", "OpenCV", "NLP", "RAG", "MLOps", "HuggingFace", "TensorRT", "CUDA"]
    },
    "AIDS": {
        "weight": 0.14,
        "skills": ["Python", "R", "SQL", "Pandas", "PowerBI", "Tableau", "PySpark", "Machine Learning", "Data Mining", "Statistics", "BigQuery", "Snowflake", "dbt"]
    },
    "ISE": {
        "weight": 0.12,
        "skills": ["Java", "Spring Boot", "Go", "AWS", "GCP", "Microservices", "REST APIs", "PostgreSQL", "CI/CD", "Linux", "Algorithms", "Terraform", "Node.js"]
    },
    "ECE": {
        "weight": 0.14,
        "skills": ["Embedded C", "C++", "Verilog", "VHDL", "ARM Cortex", "RTOS", "Linux Device Drivers", "PCB Design", "SPI", "I2C", "DSP", "SystemVerilog", "UVM"]
    },
    "EEE": {
        "weight": 0.08,
        "skills": ["MATLAB", "Simulink", "PLC/SCADA", "Power Electronics", "Embedded C", "Control Systems", "IoT", "AutoCAD Electrical", "BMS", "Inverter Design"]
    },
    "MECH": {
        "weight": 0.06,
        "skills": ["SolidWorks", "AutoCAD", "ANSYS", "CATIA", "GD&T", "Thermodynamics", "Python", "FEA", "CFD", "CAM", "Additive Manufacturing"]
    },
    "ROBOTICS": {
        "weight": 0.04,
        "skills": ["ROS2", "Python", "C++", "Gazebo", "SLAM", "Computer Vision", "Kinematics", "Microcontrollers", "LiDAR Interfacing", "Path Planning"]
    },
    "CIVIL": {
        "weight": 0.02,
        "skills": ["AutoCAD Civil 3D", "Revit", "STAAD Pro", "GIS", "Structural Analysis", "Geotechnical Modeling", "Primavera"]
    },
    "BIOTECH": {
        "weight": 0.02,
        "skills": ["Bioinformatics", "Python", "R", "Biostatistics", "CRISPR Data Analysis", "Molecular Docking", "NGS Pipelines"]
    }
}

COLLEGES = [
    "Main Campus (Bengaluru)",
    "East Campus (Tech Park)",
    "South Campus (DeepTech Lab)"
]

DOMAINS_AND_COMPANIES = {
    "Tier-1 Tech & Cloud Infrastructure": [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Adobe", "Salesforce", "Oracle",
        "Atlassian", "Uber", "Cisco", "VMware", "ServiceNow", "Intuit", "PayPal", "Twilio", "Stripe"
    ],
    "AI, Generative Systems & Big Data": [
        "NVIDIA", "OpenAI", "Synthlinx AI", "Databricks", "Snowflake", "Palantir", "Cohere",
        "Scale AI", "C3.ai", "Hugging Face", "Fractal Analytics", "Tiger Analytics", "Mu Sigma"
    ],
    "Semiconductors, VLSI & Embedded": [
        "Qualcomm", "Intel", "Texas Instruments", "AMD", "Broadcom", "MediaTek", "NXP Semiconductors",
        "Synopsys", "Cadence Design", "Arm", "Microchip Technology", "Analog Devices", "STMicroelectronics"
    ],
    "Automotive, EV & Robotics": [
        "Tesla", "Tata Motors", "Mahindra & Mahindra", "Bosch", "Continental", "Mercedes-Benz R&D",
        "Volvo Group", "Ather Energy", "Ola Electric", "Hyundai Mobis", "ZF Group", "ABB Robotics", "Fanuc"
    ],
    "FinTech, Banking & Quant": [
        "Goldman Sachs", "Morgan Stanley", "JPMorgan Chase", "Barclays", "American Express",
        "BNY Mellon", "Deutsche Bank", "Mastercard", "Visa", "Societe Generale", "UBS"
    ],
    "Enterprise IT, Consulting & Systems": [
        "Infosys", "TCS", "Wipro", "Accenture", "Capgemini", "Cognizant", "HCLTech", "LTI-Mindtree",
        "Tech Mahindra", "IBM", "Deloitte", "PwC", "EY", "KPMG", "DXC Technology", "Persistent Systems"
    ],
    "Aerospace, Energy & Industrial": [
        "Boeing", "Airbus", "ISRO Commercial Partner", "General Electric", "Siemens", "Honeywell",
        "Schneider Electric", "L&T Heavy Engineering", "Reliance Industries", "Tata Power"
    ],
    "HealthTech, BioTech & Consumer Tech": [
        "Philips Healthcare", "GE Healthcare", "Medtronic", "Siemens Healthineers", "Biocon",
        "Novartis", "Samsung R&D", "Sony India", "Flipkart", "Swiggy", "Zomato", "Myntra"
    ]
}

DOMAIN_ROLES = {
    "Tier-1 Tech & Cloud Infrastructure": [
        "Software Development Engineer I (SDE-1)", "Backend Microservices Architect", "Cloud Platform Engineer",
        "Distributed Systems Engineer", "Site Reliability Engineer (SRE)", "Frontend Engineer (React/TypeScript)",
        "Full Stack Developer", "API Infrastructure Engineer", "Security & Identity Engineer", "DevOps Engineer"
    ],
    "AI, Generative Systems & Big Data": [
        "Generative AI Engineer", "LLM Fine-Tuning & Quantization Specialist", "RAG Pipeline Architect",
        "Machine Learning Engineer", "Computer Vision Specialist", "NLP Research Engineer", "MLOps Engineer",
        "Data Platform Engineer", "Big Data Pipeline Developer", "Applied Scientist (AI)"
    ],
    "Semiconductors, VLSI & Embedded": [
        "Firmware & Kernel Engineer", "Silicon Bring-Up Specialist", "ASIC Design Verification Engineer",
        "RTL Design Engineer", "Physical Design Engineer", "FPGA Prototyping Specialist", "Embedded C++ Developer",
        "RTOS Systems Architect", "Device Driver Engineer (Linux)", "Board Support Package (BSP) Engineer"
    ],
    "Automotive, EV & Robotics": [
        "EV Battery Management System (BMS) Engineer", "Automotive Embedded Software Developer",
        "AUTOSAR Software Architect", "CAE Simulation Engineer (FEA/CFD)", "Vehicle Dynamics Specialist",
        "ADAS Perception Engineer", "Robotics Navigation Specialist (ROS2/SLAM)", "Motor Control & Inverter Designer"
    ],
    "FinTech, Banking & Quant": [
        "Quantitative Analyst", "High-Frequency Trading (HFT) Developer", "Financial Risk Software Engineer",
        "Payment Gateway Engineer", "Blockchain & Smart Contract Developer", "Algorithmic Trading Systems Engineer"
    ],
    "Enterprise IT, Consulting & Systems": [
        "Associate Consultant (Enterprise AI)", "Specialist Programmer", "Digital Transformation Architect",
        "Cybersecurity Analyst", "Enterprise Solution Architect", "Cloud Migration Engineer", "QA Automation Architect"
    ],
    "Aerospace, Energy & Industrial": [
        "Avionics Software Engineer", "Aerodynamic Simulation Analyst", "Smart Grid Systems Engineer",
        "Industrial Automation Engineer (PLC/SCADA)", "Renewable Energy Systems Designer", "Power Electronics Design Engineer"
    ],
    "HealthTech, BioTech & Consumer Tech": [
        "Biomedical Algorithm Engineer", "Medical Imaging Software Developer", "Bioinformatics Pipeline Engineer",
        "Computational Biologist", "Consumer App Mobile Developer (iOS/Android)", "Clinical Data Specialist"
    ]
}

FIRST_NAMES = [
    "Aarav", "Priya", "Rohan", "Sneha", "Ananya", "Kiran", "Vikram", "Neha", "Aditya", "Pooja",
    "Rahul", "Divya", "Sanjay", "Meera", "Varun", "Kavya", "Siddharth", "Ishita", "Arjun", "Ritu",
    "Gaurav", "Swati", "Naveen", "Tanvi", "Akash", "Bhavya", "Harish", "Shruti", "Manish", "Deepika",
    "Nikhil", "Shreya", "Kunal", "Preeti", "Suresh", "Lakshmi", "Rakesh", "Sangeeta", "Chethan", "Mansi"
]

LAST_NAMES = [
    "Sharma", "Patel", "Iyer", "Reddy", "Roy", "Varma", "Sen", "Nair", "Kulkarni", "Hegde",
    "Deshmukh", "Bhat", "Rao", "Joshi", "Gupta", "Agarwal", "Mishra", "Choudhury", "Pillai",
    "Menon", "Banerjee", "Chatterjee", "Shetty", "Gowda", "Verma", "Pandey", "Saxena", "Bose"
]

# ----------------------------------------------------
# 3. GENERATE COMPANIES, DRIVES & JOB DESCRIPTIONS
# ----------------------------------------------------
companies_master = []
drives_list = []
jds_list = []
drive_counter = 1

for domain, comp_names in DOMAINS_AND_COMPANIES.items():
    roles_pool = DOMAIN_ROLES[domain]
    for comp in comp_names:
        if "Tier-1" in domain or "AI" in domain:
            base_ctc = round(random.uniform(18.0, 32.0), 2)
            min_cgpa = round(random.uniform(7.8, 8.5), 1)
            eligible_depts = ["CSE", "AIML", "AIDS", "ISE"]
        elif "Semiconductors" in domain:
            base_ctc = round(random.uniform(14.0, 24.0), 2)
            min_cgpa = round(random.uniform(7.5, 8.2), 1)
            eligible_depts = ["ECE", "EEE", "CSE", "ROBOTICS"]
        elif "Automotive" in domain:
            base_ctc = round(random.uniform(8.5, 16.0), 2)
            min_cgpa = round(random.uniform(6.8, 7.8), 1)
            eligible_depts = ["MECH", "ECE", "EEE", "ROBOTICS"]
        elif "FinTech" in domain:
            base_ctc = round(random.uniform(15.0, 26.0), 2)
            min_cgpa = round(random.uniform(7.5, 8.3), 1)
            eligible_depts = ["CSE", "AIML", "AIDS", "ISE"]
        elif "Enterprise" in domain:
            base_ctc = round(random.uniform(6.5, 11.0), 2)
            min_cgpa = round(random.uniform(6.0, 7.0), 1)
            eligible_depts = ["CSE", "AIML", "AIDS", "ISE", "ECE", "EEE", "MECH", "CIVIL", "BIOTECH"]
        else:
            base_ctc = round(random.uniform(8.0, 18.0), 2)
            min_cgpa = round(random.uniform(6.5, 7.5), 1)
            eligible_depts = ["CSE", "ECE", "MECH", "BIOTECH", "CIVIL"]

        companies_master.append({
            "Company": comp,
            "Domain": domain,
            "Email": f"campus-hiring@{comp.lower().replace(' ', '').replace('&', 'and')}.com",
            "Status": "Approved" if random.random() > 0.05 else "Pending",
            "Openings": random.randint(5, 50)
        })

        selected_roles = random.sample(roles_pool, random.randint(2, min(3, len(roles_pool))))
        for role in selected_roles:
            drive_id = f"DRV-{drive_counter:03d}"
            jd_id = f"JD-{drive_counter + 1000}"
            role_ctc = round(base_ctc * random.uniform(0.9, 1.15), 2)
            primary_dept = eligible_depts[0]
            req_skills = ", ".join(DEPTS[primary_dept]["skills"][:6])

            drives_list.append({
                "Drive_ID": drive_id,
                "Company": comp,
                "Role": role,
                "Min_CGPA": min_cgpa,
                "Eligible_Depts": ", ".join(eligible_depts),
                "Required_Skills": req_skills,
                "Description": f"Hiring for {role} under {domain}. Production deployment and technical ownership required.",
                "Package_LPA": role_ctc,
                "Session_Date": (datetime.now() + timedelta(days=random.randint(5, 60))).strftime("%Y-%m-%d"),
                "App_Link": f"https://careers.{comp.lower().replace(' ', '')}.com/jobs",
                "Seminar_Link": f"https://meet.google.com/{comp.lower().replace(' ', '')}-talk",
                "PPT_Link": f"https://pragyan.edu/resources/{comp.lower().replace(' ', '')}_deck.pdf"
            })

            jds_list.append({
                "JD_ID": jd_id,
                "Drive_ID": drive_id,
                "Company": comp,
                "Role": role,
                "Target_Domain": domain,
                "Full_JD_Text": f"Role: {role} at {comp} ({domain}). Requirements: {req_skills}. Responsibilities include system architecture, unit testing, and cross-functional team delivery.",
                "Min_Experience_Months": 0,
                "Package_LPA": role_ctc
            })
            drive_counter += 1

# ----------------------------------------------------
# 4. GENERATE 1,500 STUDENTS & CV CORPUS
# ----------------------------------------------------
students_list = []
cv_corpus_list = []
stages_list = []
selections_list = []
experiences_list = []

dept_keys = list(DEPTS.keys())
dept_weights = [DEPTS[d]["weight"] for d in dept_keys]
drives_df_temp = pd.DataFrame(drives_list)

for i in range(1, TOTAL_STUDENTS + 1):
    stu_id = f"STU{i:04d}"
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    name = f"{fname} {lname}"
    dept = np.random.choice(dept_keys, p=dept_weights)
    college = random.choice(COLLEGES)
    grad_year = np.random.choice([2024, 2025, 2026], p=[0.20, 0.50, 0.30])

    cgpa = round(float(np.clip(np.random.normal(7.85, 0.95), 5.5, 9.95)), 2)

    dept_skill_pool = DEPTS[dept]["skills"]
    skills = random.sample(dept_skill_pool, random.randint(4, 7))
    skills_str = ", ".join(skills)

    projects = f"Engineering capstone in {dept}: Implemented architecture prototype using {skills[0]} and {skills[1]}."
    experience = f"{random.choice(['Intern at Core Industry Partner', 'Research Assistant at PragyanAI Labs', 'Open Source Contributor', 'Academic Fellow'])} ({random.randint(2, 6)} months)."

    dream_roles = random.choice(DOMAIN_ROLES.get("Tier-1 Tech & Cloud Infrastructure" if dept in ["CSE", "ISE"] else "Semiconductors, VLSI & Embedded"))
    dream_comps = ", ".join(random.sample([c["Company"] for c in companies_master[:30]], 2))
    salary_exp = round(float(np.clip(cgpa * 2.2 + random.uniform(-1, 3), 6.0, 32.0)), 1)

    placement_prob = 0.90 if grad_year == 2024 else (0.76 if grad_year == 2025 else 0.28)
    if cgpa < 6.5:
        placement_prob *= 0.4
    elif cgpa > 8.8:
        placement_prob = min(placement_prob * 1.25, 0.98)

    is_placed = random.random() < placement_prob

    if is_placed:
        status = "Placed"
        eligible_drives = drives_df_temp[drives_df_temp["Eligible_Depts"].str.contains(dept, na=False)]
        if eligible_drives.empty:
            eligible_drives = drives_df_temp

        chosen_drive = eligible_drives.sample(1).iloc[0]
        comp_name = chosen_drive["Company"]
        role_name = chosen_drive["Role"]
        package_lpa = chosen_drive["Package_LPA"]

        selections_list.append({
            "Drive_ID": chosen_drive["Drive_ID"],
            "Company": comp_name,
            "Student_ID": stu_id,
            "Student_Name": name,
            "Dept": dept,
            "Attended": True,
            "Selection_Status": "Selected",
            "Offered_Role": role_name,
            "Offered_CTC_LPA": package_lpa
        })

        stages_list.append({
            "Stage_ID": f"STG-{i:04d}",
            "Student_ID": stu_id,
            "Student_Name": name,
            "Dept": dept,
            "Company": comp_name,
            "Role": role_name,
            "Current_Round": "Offer Extended (Selected)",
            "Next_Round_Date": "Completed",
            "Mode_Location": f"{comp_name} Corporate Campus"
        })

        if len(experiences_list) < 150:
            experiences_list.append({
                "Exp_ID": f"EXP-{len(experiences_list) + 1001}",
                "Student_ID": stu_id,
                "Student_Name": name,
                "Dept": dept,
                "Company": comp_name,
                "Role": role_name,
                "Rounds_Faced": "Round 1: Online Coding, Round 2: Architecture & LLD, Round 3: Leadership/HR",
                "Skills_Excelled": f"{skills[0]}, {skills[1]}, Low-Level Invariants",
                "Challenges_Faced": "Edge failure recovery, race conditions, and distributed caching trade-offs.",
                "Advice_To_Crack": "Dry run edge cases out loud and state algorithmic complexity assumptions upfront.",
                "Photo_Attached": True if random.random() > 0.3 else False,
                "Audio_Attached": True if random.random() > 0.2 else False,
                "Timestamp": (datetime.now() - timedelta(days=random.randint(2, 45))).strftime("%Y-%m-%d")
            })
    else:
        status = "Not Placed"
        comp_name = "None"
        role_name = "None"
        package_lpa = 0.0

        if random.random() < 0.30:
            random_drive = drives_df_temp.sample(1).iloc[0]
            stages_list.append({
                "Stage_ID": f"STG-{i:04d}",
                "Student_ID": stu_id,
                "Student_Name": name,
                "Dept": dept,
                "Company": random_drive["Company"],
                "Role": random_drive["Role"],
                "Current_Round": random.choice(["Round 1: Screening Cleared", "Round 2: Technical Interview", "Round 3: Final Managerial"]),
                "Next_Round_Date": (datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d 10:30 AM"),
                "Mode_Location": "Virtual / MS Teams"
            })

    students_list.append({
        "ID": stu_id,
        "Name": name,
        "Dept": dept,
        "College": college,
        "Grad_Year": grad_year,
        "CGPA": cgpa,
        "Skills": skills_str,
        "Projects": projects,
        "Experience": experience,
        "Linkedin": f"https://linkedin.com/in/{fname.lower()}-{lname.lower()}-{i}",
        "Github": f"https://github.com/{fname.lower()}{i}",
        "Dream_Roles": dream_roles,
        "Dream_Companies": dream_comps,
        "Salary_Expected_LPA": salary_exp,
        "Status": status,
        "Company": comp_name,
        "Role": role_name,
        "Package_LPA": package_lpa
    })

    cv_corpus_list.append({
        "Student_ID": stu_id,
        "Full_Name": name,
        "Dept": dept,
        "Parsed_Resume_Text": f"{name} ({dept}, CGPA: {cgpa}). Skills: {skills_str}. Projects: {projects}. Experience: {experience}.",
        "Extracted_Keywords": skills_str,
        "Pragyan_Readiness_Score": round(min((cgpa * 9.5) + (len(skills) * 1.2) + random.uniform(2, 6), 99.5), 1)
    })

# ----------------------------------------------------
# 5. GENERATE RECRUITER FEEDBACK & TRAINING SESSIONS
# ----------------------------------------------------
recruiter_feedback_list = [
    {
        "Company": "Google",
        "Drive_ID": "DRV-001",
        "Evaluator": "Staff Engineering Manager",
        "Dept_Evaluated": "CSE, AIML, ISE",
        "Overall_Rating": 4.3,
        "Strong_Areas": "Strong algorithmic thinking and clean Python/C++ code structure.",
        "Observed_Gaps": "Struggled with multi-threaded synchronization, concurrency locks, and distributed caching (Redis).",
        "Recommended_Curriculum_Fixes": "Include hands-on low-level system design labs and live debugging sessions."
    },
    {
        "Company": "Qualcomm",
        "Drive_ID": "DRV-025",
        "Evaluator": "Senior Director of Silicon Software",
        "Dept_Evaluated": "ECE, EEE",
        "Overall_Rating": 3.9,
        "Strong_Areas": "Good basic digital design and state machine understanding.",
        "Observed_Gaps": "Lack of hands-on pointer arithmetic in bare-metal C and RTOS scheduler mechanics.",
        "Recommended_Curriculum_Fixes": "Introduce hardware-in-the-loop debugging with ARM Cortex-M microcontrollers."
    },
    {
        "Company": "Synthlinx AI",
        "Drive_ID": "DRV-019",
        "Evaluator": "Head of AI Research",
        "Dept_Evaluated": "AIML, AIDS",
        "Overall_Rating": 4.5,
        "Strong_Areas": "Excellent grasp of RAG chunking and vector index retrieval.",
        "Observed_Gaps": "Need deeper exposure to LLM quantization, KV-caching, and inference engine latency benchmarking.",
        "Recommended_Curriculum_Fixes": "Run production agent deployment hackathons with LangGraph and FastEngine."
    },
    {
        "Company": "Tesla",
        "Drive_ID": "DRV-038",
        "Evaluator": "Lead Powertrain Architect",
        "Dept_Evaluated": "MECH, ROBOTICS, EEE",
        "Overall_Rating": 4.1,
        "Strong_Areas": "Strong CAD geometric modeling and thermal calculations.",
        "Observed_Gaps": "Need stronger proficiency in automated telemetry scripting using Python and CAN bus protocols.",
        "Recommended_Curriculum_Fixes": "Integrate cross-disciplinary hardware-software labs."
    }
]

training_sessions_list = [
    {
        "Session_ID": "TRN-101",
        "Type": "Bootcamp",
        "Title": "Generative AI & Agentic Workflows with LangGraph",
        "Target_Depts": "CSE, AIML, AIDS, ISE",
        "Instructor": "Dr. Sateesh Ambesange (PragyanAI)",
        "Schedule_Date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "Timing": "10:00 AM - 04:00 PM",
        "Mode": "Hybrid",
        "Location": "Pragyan DeepTech Lab / Zoom",
        "Curriculum": "1. Multi-Agent Swarms 2. Vector DB Indexing 3. Production RAG 4. FastEngine APIs",
        "Meeting_Link": "https://zoom.us/j/pragyan-genai-bootcamp",
        "Resource_Link": "https://github.com/pragyan-ai/agentic-curriculum-2026"
    },
    {
        "Session_ID": "TRN-102",
        "Type": "Workshop",
        "Title": "Bare-Metal ARM Firmware & RTOS Preemption Intensive",
        "Target_Depts": "ECE, EEE, ROBOTICS",
        "Instructor": "Lead Architect (Qualcomm)",
        "Schedule_Date": (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
        "Timing": "09:30 AM - 01:30 PM",
        "Mode": "Offline",
        "Location": "Embedded Systems Lab (Block B)",
        "Curriculum": "1. ARM Cortex-M Register Mapping 2. Mutexes & Priority Inversion 3. Custom SPI Drivers",
        "Meeting_Link": "N/A (Physical Event)",
        "Resource_Link": "https://pragyan.edu/resources/arm_firmware_workshop.pdf"
    },
    {
        "Session_ID": "TRN-103",
        "Type": "Masterclass",
        "Title": "Distributed Systems & Raft Consensus in High-Scale FinTech",
        "Target_Depts": "CSE, ISE, AIDS",
        "Instructor": "Principal Systems Engineer (Amazon)",
        "Schedule_Date": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
        "Timing": "02:00 PM - 05:00 PM",
        "Mode": "Online",
        "Location": "Google Meet",
        "Curriculum": "1. Partition Tolerance 2. Log Replication 3. High-Throughput RPCs",
        "Meeting_Link": "https://meet.google.com/distributed-systems-talk",
        "Resource_Link": "https://pragyan.edu/resources/distributed_consensus.pdf"
    }
]

# ----------------------------------------------------
# 6. WRITE ALL CSV FILES
# ----------------------------------------------------
datasets = {
    "students.csv": students_list,
    "companies.csv": companies_master,
    "drives.csv": drives_list,
    "job_descriptions.csv": jds_list,
    "student_cv_corpus.csv": cv_corpus_list,
    "candidate_stages.csv": stages_list,
    "drive_selections.csv": selections_list,
    "interview_experiences.csv": experiences_list,
    "recruiter_feedback.csv": recruiter_feedback_list,
    "training_sessions.csv": training_sessions_list
}

for filename, data in datasets.items():
    file_path = os.path.join(DATA_DIR, filename)
    pd.DataFrame(data).to_csv(file_path, index=False)
    print(f"Generated data/{filename} ({len(data)} rows)")

print(f"\nCreated {len(datasets)} dataset files under '{DATA_DIR}'.")
