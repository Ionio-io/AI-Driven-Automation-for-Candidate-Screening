import streamlit as st
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.chains import LLMChain
import requests

load_dotenv()

# Initialize session state
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.analysis_done = False
    st.session_state.show_phone_input = False


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
    person based on the provided {information} resume details. In the end, conclude whether the
      person is suitable for the {role} role. Only consider the
      candidate for acceptance if they possess relevant skills or passion
        for the job role; otherwise, reject them. Provide strong reasons for
     whether you accept or reject the candidate. 
     The conclusion should be clear and concise and start with a heading 'Conclusion'. Also based on the 
     resume in context of it generate 2 questions that needs to be asked for better understanding totally in context
     with the provided information {information} to assess the candidate
    It should follow this pattern - 
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
    ask the candidate about their experience in mention any relevant experience or skills that are important for the job role.
    based on the information provided in the resume, ask the candidate about their interest in mention any relevant interests or activities related to the job role.
    
    """
    summary_prompt = PromptTemplate(
        input_variables=["information", "role"], template=summary_template
    )
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5)
    chain = LLMChain(llm=llm, prompt=summary_prompt)
    result = chain.invoke(input={"information": information, "role": role})
    summary = result["text"]
    return summary


def inicall(phone_no):
    url = "https://api.bland.ai/v1/calls"
    payload = {
        "phone_number": phone_no,
        "task": "The main objective of this phone interview is to gather additional information about the candidate who has been shortlisted based on their resume. The goal is to assess the candidate's qualifications, experiences, and overall suitability for the job role.",
        "first_sentence": "Hello, I'm calling from OpenAI regarding the application you expressed interest in. Could you confirm if this is a convenient time to speak?",
        "wait_for_greeting": True,
        "model": "base",
        "tools": [],
        "record": True,
        "voice_settings": {},
        "language": "eng",
        "answered_by_enabled": True,
        "temperature": 0,
        "amd": False,
    }
    headers = {
        "authorization": "sk-zkic20236xlh90oguo8fek0aclmpnrv0t8youl8yc8lt0lkvnniffsmzlyd8yhul69",
        "Content-Type": "application/json",
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response_json = response.json()
    return response_json.get("message", "")


def main():
    # Add image at the top
    st.image("/Users/shivammitter/Desktop/Home/AI/Gen_AI/projects/resume-llm/p.jpeg", use_column_width=True)

    st.title("Resume Analysis")
    st.header("Upload a PDF Resume")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    role = st.text_input("Specify the role")

    if st.button("Analyse the Resume"):
        if uploaded_file is not None:
            # Process the uploaded PDF
            process_pdf(uploaded_file)
            # Call LLMcall function to analyze the resume
            summary = LLMcall(role)
            # Display the result
            st.session_state.analysis_done = True
            st.subheader("Analysis Result")
            st.write(summary)
        else:
            st.write("Please upload a PDF file before analyzing.")

    if st.session_state.analysis_done:
        if not st.session_state.show_phone_input:
            st.button("Initiate Phone Interview")
            st.session_state.show_phone_input = True
        else:
            phone_no = st.text_input("Enter phone number with the country code")
            if phone_no:
                message = inicall(phone_no)
                st.write("Message from API:", message)
            else:
                st.write(
                    "Please enter a phone number before initiating the phone interview."
                )


if __name__ == "__main__":
    main()
