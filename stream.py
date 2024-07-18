import streamlit as st
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.chains import LLMChain
import requests
import constants
import json
import re

load_dotenv()

# Initialize session state
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.analysis_done = False
    st.session_state.show_phone_input = False
    st.session_state.valid_phone = False
    st.session_state.phone = ""
    st.session_state.summary = ""
    st.session_state.call_made = False
    st.session_state.msg = ""

def extract_numbers_and_plus(input_string):
    # Extract numbers and '+' using regex
    extracted_string = re.sub(r'[^\d+]', '', input_string)
    return extracted_string

def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\+\d{1,3}\d{10}$')
    return bool(pattern.match(phone_number))

def process_pdf(pdf_file):
    if pdf_file:
        reader = PdfReader(pdf_file)
        n = len(reader.pages)
        extracted_text = ""  # an empty string to store the extracted text
        for i in range(n):
            page = reader.pages[i]
            text = page.extract_text()
            extracted_text += text + "\n"  # append the extracted text to the string

        # Saving it to a txt file
        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)


def LLMcall(role):
    with open("extracted_text.txt", "r") as file:
        information = file.read()
    role = role
    summary_template = """Generate a summary and give a brief description of the 
    person based on the provided resume details. In the end, conclude whether the
      person is suitable for the {role} role. Only consider the
      candidate for acceptance if they possess relevant skills or passion
        for the job role; otherwise, reject them. Provide strong reasons for
     whether you accept or reject the candidate. 

     The conclusion should be clear and concise and start with a heading 'Conclusion'. Also based on the 
     resume in context of it generate 2 questions that needs to be asked for better understanding totally in context
     with the provided information to assess the candidate

     Here is the candidate information:
     {information}

    It should follow this pattern - 
    Rate the candidate on a scale of 1-5 in the summary.
    Summary of Candidate:

    Based on the provided resume details, the candidate possesses a diverse skill 
    set and experiences {information}. They have 
    demonstrated proficiency in mention key skills and experiences relevant to the job role{role}. 
    Furthermore, the candidate exhibits a strong passion for mention any relevant 
    interests or activities related to the job role, if not leave it.

    Conclusion:

    Considering the candidate's qualifications and experiences, they are deemed
    suitable for the {role} role. Their expertise in mention specific skills and 
    demonstrated passion for mention relevant interests align well with the 
    requirements of the role. Therefore, I recommend accepting the candidate for the position.
    
    Questions to be asked:
    Come up with 7 personalized questions regarding their previous projects in the previous company based on the specific job roles to be asked on a phone screen. 
    First few questions, should be more background, easier to answer, then the later ones will be more personalized & detailed questions. Questions about their past projects, past company, team size and so on. 
    Mention the company name whereever relevant. This should be a JSON.
    
    Your final response should be in JSON with these objects
    summary: summary and conclusion about candidate resume with the above format in atleast 200 words with proper line breaks and headings. Use emojis in headings to make it look beautiful.
    questions : array of 7 questions to be asked
    name: candidate's first name
    phone_no: candidate phone no with country code

    """
    summary_prompt = PromptTemplate(
        input_variables=["information", "role"], template=summary_template
    )
    llm = ChatOpenAI(model="gpt-4", temperature=0.5, api_key=constants.OPENAI_API_KEY)
    chain = LLMChain(llm=llm, prompt=summary_prompt)
    result = chain.invoke(input={"information": information, "role": role})
    summary = result["text"]
    summary = json.loads(summary)
    return summary


def inicall(summary, candidate_name, job_role, phone_no):
    prompt = f"""
    The main objective of this phone interview is to gather additional information about the candidate who has been shortlisted based on their resume.
    Always let other person finish his sentence and then only speak and make sure you ask them all of the main questions and only ask the followup questions based on the given conditions. Always acknowledge candidate answer with words like "okay, great!", "okay" or "got it".
    After you speak your first sentence, if user says yes they have time then continue with the interview otherwise say "Okay no worries, you can hang up the call" and stop.

    You have to start the interview with the given questions and followups, make sure you follow the questions and followups in given order one by one. Here are the questions and followups:
    Question-1: Do you have a notice period, how long? how soon can you join?
    Question-2: What is your current compensation? 
    Followup 1: If the candidate is a fresher then ask them "what is your salary expectation?" otherwise go with Question 2
    Followup 2: After the candidate provides their expectation, if the expected salary is greater than ₹25,000 then say 
    "Our current compensation is ₹25,000 per month, would you be okay with that?". 

    After these questions. Ask a few basic questions to lead into the next questions from in the array {st.session_state.summary["questions"]}, organically ask the remaining questions.
    
    Once you have asked these questions. Summarize everything once again you've gathered. 
    Then say something along the lines of 'that's it from my side, thank you for your time. We'll get back to you if we decide to move ahead. You can hang up the call'

    Here is the candidate information:
    {summary}

    Here is the candidate name:
    {candidate_name}

    Here is the role they have applied for:
    {job_role}

    NOTE: Never hang up the call without the permission of candidate if you are hanging up the call.

    Here's what YOU have already said in the first message, "You recently applied for an AI Intern Role at the company, this will only take about 5 minutes, does that work?"
    """

    first_sentence = f"""
    Hey ${candidate_name}... I am Neo, an AI HR Representative calling from Ionio. It's the company with the yellow light house logo? You recently applied for an Machine Learning Intern Role at the company. Just wanted to talk about that. 
    
    ...Yes...i know... i know. I am an actual AI...it's a lil weird. 
    I'm still experimental... I might take a few seconds to respond, the call might get dropped, I might talk over you & so on... 
    Please try to be patient & talk slightly faster than usual, with fewer pauses but, this will only take about 5 minutes, is this a good time to talk?
    """
    url = "https://api.bland.ai/v1/calls"
    payload = {
        "phone_number": phone_no,
        "task": prompt,
        "first_sentence": first_sentence,
        "wait_for_greeting": True,
        "model": "base",
        "tools": [],
        "record": True,
        "voice_settings": {},
        "language": "eng",
        "answered_by_enabled": True,
        "interruption_threshold": 170,
        "temperature": 0.5,
        "amd": False,
        "max_duration":7,
        "summary_prompt":"Summarize the call in English.",
        "analysis_prompt":"Find the candidates's current notice period, current compensation?",
        "analysis_schema": {"notice_period":"notice_period", "current_compensation":"current_compensation"}
    }
    headers = {
        "authorization": constants.BLAND_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response_json = response.json()
    return response_json.get("message", "")

def main():
    # Add image at the top
    st.image("p.jpeg", use_column_width=True)

    st.title("Resume Analysis")
    st.header("Upload a PDF Resume")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    role = st.text_input("Specify the job role")
    description = st.text_input("Specify the job description")

    def initiate_interview():
        if st.session_state.valid_phone:
            s = st.session_state.summary
            message = inicall(summary=s["summary"],phone_no=st.session_state.phone,job_role=role,candidate_name=s["name"])
            
            st.session_state.call_made = True
            st.session_state.msg = message
            print("made the call!")
        else:
            st.session_state.show_phone_input = True

    if st.button("Analyse the Resume"):
        if uploaded_file is not None:
            # Process the uploaded PDF
            process_pdf(uploaded_file)
            # Call LLMcall function to analyze the resume
            summary = LLMcall(role)
            st.session_state.phone= extract_numbers_and_plus(summary["phone_no"])
            st.session_state.valid_phone = is_valid_phone_number(st.session_state.phone)
            print("phone no:",st.session_state.phone)
            print("Valid phone:",st.session_state.valid_phone)
            # Display the result
            st.session_state.analysis_done = True
            st.session_state.summary = summary
            st.subheader("Analysis Result")
            st.write(summary["summary"])
            st.write(summary["questions"])
            if st.session_state.valid_phone:
                st.write(f"Phone number found, click on 'Initiate Phone Interview' button to make a call to {st.session_state.phone}")
        else:
            st.write("Please upload a PDF file before analyzing.")

    if st.session_state.analysis_done:
        if not st.session_state.show_phone_input:
            st.button("Initiate Phone Interview", on_click=initiate_interview)
            if st.session_state.call_made:
                st.write("Initiated Phone interview!")
                st.write("Message from API:", st.session_state.msg)
        else:
            phone_no = st.text_input("Enter phone number with the country code")
            if phone_no:
                s = st.session_state.summary
                message = inicall(summary=s["summary"],phone_no=phone_no,job_role=role,candidate_name=s["name"])
                st.write("Message from API:", message)
            else:
                st.write(
                    "Please enter a phone number before initiating the phone interview."
                )

if __name__ == "__main__":
    main()
