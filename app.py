import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date

# Load API key from Streamlit secrets
MONGO_CONNECTION_STRING = st.secrets["MongoDB"]["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
db = client["database"]
collection = db["employees"]

# Enums
SalaryCurrencyEnum = ["PKR", "USD", "EUR"]
SalaryTypeEnum = ["Hourly", "Monthly"]
JobTypeEnum = ["Full-Time", "Part-Time", "Contract"]
GenderEnum = ["Male", "Female", "Other"]
JoiningEnum = ["Immediate", "1 Month", "2 Months", "3 Months"]

def get_or_create_location(location_name):
    """Gets or creates a location in the 'addresses' collection."""
    addresses_collection = db["addresses"]
    existing = addresses_collection.find_one({"name": location_name})
    return existing["_id"] if existing else addresses_collection.insert_one({"name": location_name}).inserted_id

def get_or_create(collection_name, field_name, value):
    """Gets or creates a document in a collection."""
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
    date_of_birth = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
    salary_currency = st.selectbox("Salary Currency", SalaryCurrencyEnum)
    seeking_job_type = st.selectbox("Seeking Job Type", JobTypeEnum)
    seeking_range = st.number_input("Seeking Range (km)", min_value=0)
    is_radar = st.checkbox("Enable Radar Mode")
    gender = st.selectbox("Gender", GenderEnum)
    slogan = st.text_input("Slogan")

    required_skills = st.text_area("Skills (comma separated)")
    verified_skills = st.text_area("Verified Skills (comma separated)")

    # New Fields
    years_of_experience = st.number_input("Years of Experience", min_value=0)
    last_degree = st.text_input("Last Degree")
    certifications = st.text_area("Certifications (comma separated)")
    joining = st.selectbox("Joining", JoiningEnum)
    location_name = st.text_input("Location") # Changed to text_input
    is_verified = st.checkbox("Is Verified")

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
        if not location_name.strip():  # Check for empty location
            errors.append("Location is required.")


        required_skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        verified_skills_list = [skill.strip() for skill in verified_skills.split(",") if skill.strip()]
        certifications_list = [cert.strip() for cert in certifications.split(",") if cert.strip()]

        if not required_skills_list:
            errors.append("At least one Required Skill is needed.")
        if not verified_skills_list:
            errors.append("At least one Verified Skill is needed.")


        if errors:
            for error in errors:
                st.error(error)
        else:
            # Create or get the location ID
            final_location = get_or_create_location(location_name.strip())

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
                "requiredSkills": [get_or_create("skills", "name", skill) for skill in required_skills_list],
                "verifiedSkills": [get_or_create("skills", "name", skill) for skill in verified_skills_list],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "yearsOfExperience": years_of_experience,
                "lastDegree": last_degree,
                "certifications": [get_or_create("certifications", "name", cert) for cert in certifications_list],
                "joining": joining,
                "addressId": final_location,
                "isVerified": is_verified,
            }
            collection.insert_one(employee_data)
            st.success("Profile submitted successfully!")
