# AI-Enabled Candidate Evaluation
---
## Overview

This project aims to revolutionize the candidate selection process by leveraging Google's Gemini Pro and Phone call platform Bland.ai . In the fast-paced world of recruitment, traditional methods can be inefficient and time-consuming. With the integration of AI, we streamline resume screening, phone interviews, and candidate evaluation, enhancing efficiency and improving the quality of hires.
<img width="608" alt="image" src="https://github.com/Ionio-io/AI-Driven-Automation-for-Candidate-Screening/assets/91791239/4e26f85c-6b40-4e26-9e27-748067319aef">

---
## Key Features

- **AI-Powered Resume Screening**: Utilizes the GPT-3.5 model to analyze resumes and provide a detailed summary, conclusion, and relevant questions for initial screening.
  
- **Automated Phone Interviews**: Integrates with Bland.ai to conduct phone interviews, customizing tasks and greetings for a tailored candidate experience.

- **Interactive Chatbots**: AI-powered chatbots provide real-time responses to candidates' queries, enhancing their experience and engagement throughout the recruitment process.

- **Personalized Candidate Recommendations**: AI analyzes candidates' profiles and preferences to recommend personalized job opportunities, improving the candidate matching process.

- **Onboarding and Training Plans**: AI assesses new hires' skills and identifies knowledge gaps, recommending targeted training programs to accelerate their integration into the company.
---
### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Ionio-io/AI-Driven-Automation-for-Candidate-Screening.git
   ```

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Step 1: Resume/CV Upload and Extraction

- Upload the resume/CV and extract the text using the PyPDF library. The extracted text will be stored in a text file named “extracted_text.txt”.

### Step 2: Job Role Input

- Specify the job role for which the candidate is being evaluated, assigning the {role} variable.

### Step 3: Large Language Model (LLM) Analysis

- Pass the extracted resume/CV text and the specified job role to the "gpt-3.5-turbo-0125" model.
  
### Step 4: Initial Screening Decision

- Based on the LLM's final conclusion, decide whether to proceed with the application, completing the first phase of screening.

### Step 5: Phone Interview

- Utilize the Bland.ai service to conduct a phone interview, customizing tasks and greetings for a tailored candidate experience.

### Step 6: Final Conclusion

- Provide the phone interview transcript to the LLM again to generate a final conclusion on the candidate's suitability for the role.

---

## License

This project is licensed under the MIT License.

---
