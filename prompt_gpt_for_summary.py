from openai import OpenAI
from pdfminer.high_level import extract_text
import json
import os
import csv
import re
from utilities import *
import threading


PERSONS_RECOMENDATION_DATA_FILE = "persons_recomendation_data1.csv"
PERSONS_FOLDER_PATH ='./people/'
COURSE_FILE_PATH = 'ADC Manufacturing_Pharma_brochure-TEST.pdf'
COURSE_FILE_PAGE_NUMBER = 1
OPEN_AI_API_KEY = "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"
PROMPT_FOR_SUMMARY = "Please summarize the following course information text into exactly 150 words in a cohesive paragraph that includes a description of the course, its benefits, the target audience, and the ideal qualities of a potential buyer. Here is the course information text:\n"
PROMPT_FOR_RECOMMENDATION = "Given the following information about a course and a person's details, provide a recommendation score for the course on a scale of 0 to 10. The recommendation should be based on how well the course aligns with the person's background, interests, and goals. Output only the result in a dictionary format like this: `result = {recommendation: 0-10}`.\n"


MODEL_LOCK = threading.Lock()

def extract_text_from_pdf(pdf_path, page_number=1):
    text = extract_text(pdf_path, page_numbers=[page_number])
    return text

def ask_to_model(prompt):
    with MODEL_LOCK:
        try:
            return client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e:
            print(f"Error getting summary from OpenAI: {e}")
            return ""

def get_summary_from_prompt(prompt):
    return ask_to_model(prompt)

def save_summary_to_file(summary, filename="summary.txt"):
    try:
        with open(filename, "w") as f:
            f.write(str(summary.choices[0].message.content))
        print(f"Summary saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving summary to file: {e}")

def save_person_extracted_data_to_file(person_details, filename="person.json"):
    try:
        with open(filename, "w") as json_file:
            json.dump(person_details, json_file, indent=4)
        print(f"Summary saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving summary to file: {e}")

def extract_persons_information_and_get_course_recommendation(course_summary):
    person_files = [f for f in os.listdir(PERSONS_FOLDER_PATH) if os.path.isfile(os.path.join(PERSONS_FOLDER_PATH, f)) and f.endswith('.json')]
    if len(person_files) != 0:
        for person_file in person_files:
            # print(f"Processing {person_file} =============")
            person_details = read_person_file(os.path.join(PERSONS_FOLDER_PATH, person_file))
            recommendation_prompt_result = get_course_recommendation_prompt(course_summary, person_details)
            extract_recommendation_and_save_into_file(person_file, person_details['person_name'], recommendation_prompt_result)
            
    else:
        print("No Persons Json file in given directory : ", + PERSONS_FOLDER_PATH)
    
def read_person_file(person_file_name):
    dict = {}
    try:
        with open(person_file_name, 'r') as file:
            person_data = json.load(file)
            dict["person_name"] = extract_person_name(person_file_name, person_data)
            dict["person_summary"] = extract_person_summary(person_file_name, person_data)
            dict["current_position_details"] = extract_current_position_details(person_file_name, person_data)
            dict["education-field-of-study"] = extract_education_fields_of_study(person_file_name, person_data)
            dict["person_skills"] = extract_person_skills(person_file_name, person_data)
            dict["person_projects"] = extract_person_projects(person_file_name, person_data)
            # save_person_extracted_data_to_file(dict)
            return dict
    except Exception as e:
        print(f"Error in {person_file_name} while read_person_file, the error : {e}")
        return dict

def get_course_recommendation_prompt(course_summary, person_details):
    prompt = PROMPT_FOR_RECOMMENDATION + "Course Summary : " + course_summary + "\nPerson Details : " + json.dumps(person_details)
    return ask_to_model(prompt)

def save_recommendation_into_file(person_file_name, person_name, recommendation, recommendation_string):
    try:
        file_exists = os.path.isfile(PERSONS_RECOMENDATION_DATA_FILE)
        with open(PERSONS_RECOMENDATION_DATA_FILE, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['Person_File_Name', 'Person Name', 'Recommendation']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # If the file doesn't exist, write header first
            if not file_exists:
                writer.writeheader()
            writer.writerow({'Person_File_Name': person_file_name, 'Person Name': person_name, 'Recommendation': recommendation})
    except Exception as e:
        print(recommendation_string, recommendation)
        print(f"Error in {person_file_name} while save_recommendation_into_file, the error : {e}")
        
def extract_recommendation_and_save_into_file(person_file_name, person_name, recommendation_prompt_result):
    recommendation_pattern = r'\{recommendation:\s*(\d+)\}'
    content = recommendation_prompt_result.choices[0].message.content.strip()
    clean_content = content.replace("\n", "").replace(" ", "")
    recommendation_match = re.search(recommendation_pattern, clean_content)
    if recommendation_match:
        recommendation = recommendation_match.group(1)
        save_recommendation_into_file(person_file_name, person_name, recommendation, clean_content)
    else:
        print(f"Error in {person_file_name} while extract_recommendation_and_save_into_file, the error : 'Recomendation Not Found.'")
        return
    
if __name__ == "__main__":
    client = OpenAI(api_key=OPEN_AI_API_KEY)

    # extract text from pdf
    extracted_text_from_pdf = extract_text_from_pdf(COURSE_FILE_PATH, COURSE_FILE_PAGE_NUMBER)
    final_prompt = PROMPT_FOR_SUMMARY + extracted_text_from_pdf
    # print(final_prompt)
    course_summary_result = get_summary_from_prompt(final_prompt)
    # print(course_summary)
    if course_summary_result:
        course_summary = str(course_summary_result.choices[0].message.content)
        extract_persons_information_and_get_course_recommendation(course_summary)
        # save_summary_to_file(course_summary)
    else:
        print("No summary generated. Check for errors in PDF extraction or OpenAI call.")
    

