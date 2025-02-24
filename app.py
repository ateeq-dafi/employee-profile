import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# Load API key from Streamlit secrets
MONGO_CONNECTION_STRING = st.secrets["MongoDB"]["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
db = client["employees_database"]
collection = db["employees"]

# Enums
SalaryTypeEnum = ["Hourly", "Monthly"]
JobTypeEnum = ["Full Time", "Part Time"]
GenderEnum = ["Male", "Female", "Other"]

def get_or_create(collection_name, field_name, value):
    collection = db[collection_name]
    existing = collection.find_one({field_name: value})
    return existing["_id"] if existing else collection.insert_one({field_name: value}).inserted_id

st.set_page_config(page_title="Employee Profile Submission")
st.title("Employee Profile Submission")

with st.form("employee_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    industry_name = st.text_input("Industry Name")
    designation_name = st.text_input("Designation Name")
    contact = st.text_input("Contact")
    current_salary = st.number_input("Current Salary", min_value=0.0)
    min_expected_salary = st.number_input("Min Expected Salary", min_value=0.0)
    max_expected_salary = st.number_input("Max Expected Salary", min_value=0.0)
    about = st.text_area("About")
    salary_type = st.selectbox("Salary Type", SalaryTypeEnum)
    date_of_birth = st.date_input("Date of Birth")
    salary_currency = st.text_input("Salary Currency")
    seeking_job_type = st.selectbox("Seeking Job Type", JobTypeEnum)
    seeking_range = st.number_input("Seeking Range (km)", min_value=0)
    is_radar = st.checkbox("Enable Radar Mode")
    gender = st.selectbox("Gender", GenderEnum)
    slogan = st.text_input("Slogan")
    
    submitted = st.form_submit_button("Submit Profile")
    
    if submitted:
        errors = []
        if not first_name.strip():
            errors.append("First Name is required.")
        if not last_name.strip():
            errors.append("Last Name is required.")
        if not industry_name.strip():
            errors.append("Industry Name is required.")
        if not designation_name.strip():
            errors.append("Designation Name is required.")
        if not contact.strip():
            errors.append("Contact is required.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            employee_data = {
                "firstName": first_name,
                "lastName": last_name,
                "industryId": get_or_create("industries", "name", industry_name),
                "designationId": get_or_create("designations", "name", designation_name),
                "contact": contact,
                "currentSalary": current_salary,
                "minExpectedSalary": min_expected_salary,
                "maxExpectedSalary": max_expected_salary,
                "about": about,
                "salaryType": salary_type,
                "dateOfBirth": datetime.combine(date_of_birth, datetime.min.time()),
                "salaryCurrency": salary_currency,
                "seekingJobType": seeking_job_type,
                "seekingRange": seeking_range,
                "isRadar": is_radar,
                "gender": gender,
                "slogan": slogan,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            collection.insert_one(employee_data)
            st.success("Profile submitted successfully!")
