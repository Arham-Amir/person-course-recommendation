def extract_person_name(person_file_name, person_data):
    try:
        return person_data["fullName"]
    except Exception as e:
        print(f"Error in {person_file_name} while extract_person_name, the error : {e}")
        return ""
    
def extract_person_summary(person_file_name, person_data):
    try:
        return person_data["summary"]
    except Exception as e:
        print(f"Error in {person_file_name} while extract_person_summary, the error : {e}")
        return ""
    
def extract_current_position_details(person_file_name, person_data):
    dict = {}
    try:
        dict['current-position-job-title'] = person_data["currentPositions"][0]["title"]
        dict['current-position-job-description'] = person_data["currentPositions"][0]["description"]
        dict['current-position-industry'] = person_data["currentPositions"][0]["companyUrnResolutionResult"]["industry"]
        return dict
    except Exception as e:
        print(f"Error in {person_file_name} while extract_current_position_details, the error : {e}")
        return dict
    
def extract_education_fields_of_study(person_file_name, person_data):
    eductaion_fields_list = []
    try:
        for education in person_data["educations"]:
            if "fieldsOfStudy" in education:
                eductaion_fields_list.extend(education["fieldsOfStudy"])
        return eductaion_fields_list
    except Exception as e:
        print(f"Error in {person_file_name} while extract_education_fields_of_study, the error : {e}")
        return eductaion_fields_list
    
def extract_person_skills(person_file_name, person_data):
    person_skills_list = []
    try:
        for skill in person_data["skills"]:
            if "name" in skill:
                person_skills_list.append(skill["name"])
        return person_skills_list
    except Exception as e:
        print(f"Error in {person_file_name} while extract_person_skills, the error : {e}")
        return person_skills_list
        
def extract_person_projects(person_file_name, person_data):
    person_projects_list = []
    try:
        for project in person_data["projects"]:
            project_info = {
                    "title": project.get("title", ""),
                    "description": project.get("description", "")
                }
            person_projects_list.append(project_info)
        return person_projects_list
    except Exception as e:
        print(f"Error in {person_file_name} while extract_person_projects, the error : {e}")
        return person_projects_list
        