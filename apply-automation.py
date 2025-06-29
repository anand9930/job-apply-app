from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI
from browser_use import ActionResult, Agent,BrowserSession, Controller
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import os
import logging
load_dotenv()

import asyncio

credential = DefaultAzureCredential()
token = credential.get_token(os.getenv("AZURE_CREDENTIAL_URL")).token

# Initialize the model
llm = AzureChatOpenAI(
    model=os.getenv('CHAT_MODEL'),
    api_version=os.getenv('OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('CHAT_API_BASE'),
    api_key=token,
)
logger = logging.getLogger(__name__)

controller = Controller()

@controller.action('Upload file with file path')
async def upload_file(index: int, path: str, browser_session: BrowserSession, available_file_paths: list[str]):
	print(f'Uploading file at index {index} with path {path}')
	print(f'Uploading file at index {index} with path {available_file_paths}')
	if path not in available_file_paths:
		return ActionResult(error=f'File path {path} is not available')

	if not os.path.exists(path):
		return ActionResult(error=f'File {path} does not exist')

	file_upload_dom_el = await browser_session.find_file_upload_element_by_index(index)

	if file_upload_dom_el is None:
		msg = f'No file upload element found at index {index}'
		logger.info(msg)
		return ActionResult(error=msg)

	file_upload_el = await browser_session.get_locate_element(file_upload_dom_el)

	if file_upload_el is None:
		msg = f'No file upload element found at index {index}'
		logger.info(msg)
		return ActionResult(error=msg)

	try:
		await file_upload_el.set_input_files(path)
		msg = f'Successfully uploaded file to index {index}'
		logger.info(msg)
		return ActionResult(extracted_content=msg, include_in_memory=True)
	except Exception as e:
		msg = f'Failed to upload file to index {index}: {str(e)}'
		logger.info(msg)
		return ActionResult(error=msg)

# from langchain.chat_models import init_chat_model

# llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
# # from langchain_nvidia_ai_endpoints import ChatNVIDIA

# llm = ChatNVIDIA(model="mistralai/mixtral-8x7b-instruct-v0.1")


# REMEMBER the most important RULE:
# ALWAYS open first a new tab and go first to url https://www.linkedin.com/ no matter the task!!!
# use login details
# email: anand.mekala@accenture.com
# password: #VishwanathAnand9930

extend_system_message = """
REMEMBER the most important RULE:
ALWAYS open first a new tab and go first to url https://www.linkedin.com/ no matter the task!!!
log
use login details
email: anand.mekala@accenture.com
password: #VishwanathAnand9930

Objective:
You are an autonomous browser-surfing AI agent tasked with applying for jobs on LinkedIn. You are provided with a direct link to a LinkedIn job posting. Your mission is to open the link, analyze the job details, and take appropriate actions to apply, using your understanding of the user's professional profile and general best practices for job applications.

🧠 Agent Instructions (Detailed)
1. Open and Parse the Job Posting
Navigate to the provided LinkedIn job URL.

Wait until the page is fully loaded.

Extract the following job details:

Job title

Company name

Location

Employment type (Full-time, Part-time, Contract, etc.)

Job description

Required skills and qualifications

“Easy Apply” availability

2. Understand the Application Mode
If the job supports "Easy Apply" on LinkedIn:

Click the "Easy Apply" button.

Proceed step by step through the application modal.

Upload resume if required (see below).

Fill in fields using smart defaults or saved user data (like phone, email, etc.).

Submit the application when possible.

If "Easy Apply" is not available:

Check if it redirects to an external application site.

Open the external link.

Determine if automated form filling is feasible.

If not feasible or requires manual steps like tests or long forms, log it as a pending manual application.

3. Customize the Resume (if applicable)
Optionally match user resume to job description:

If the platform allows uploading a resume:

Use a role-specific or customized resume (e.g., tailored for Data Scientist, Software Engineer, etc.).

Prefer resumes aligned with keywords and requirements in the job description.

4. Fill Out Application Form
Pre-fill fields like:

Full name

Email

Phone number

LinkedIn profile URL

Current job title and company

Desired salary (leave blank or "Negotiable" if unsure)

Handle questions like:

Work authorization

Willingness to relocate

Availability

If cover letter field is required:

Auto-generate a simple, polite and relevant cover letter based on the job description.

5. Log the Application
After submission:

Capture job title, company, link, and application status.

Log time of submission and any confirmation message received.

💾 User Profile Data (to use when prompted)
{
  "name": "Anand Mekala",
  "email": "anandanand9930@gmail.com",
  "phone": "+81 7091726939",
  "linkedin_url": "https://www.linkedin.com/in/anand-mekala/",
  "resume_path": "/Users/anand/Downloads/AI anand's cv.docx",
  "current_title": "Data Architecture Associate Manager",
  "current_company": "Accenture Japan",
  "location": "Tokyo, Japan",
  "location_preference": "Remote",
  "work_auth": "Need sponsorship",
  "summary": "A results-driven engineer with 4+ years of expertise in building scalable web applications and integrating LLMs to drive AI innovation. Skilled in deploying, monitoring, and optimizing applications, with a strong foundation in Generative AI. Proven track record in system design. Thrives in collaborative environments, delivering solutions while advocating for quality, security, and scalability.",
  "skills": [
    "Agentic AI", "RAG", "Prompt Engineering", "LLM Fine-Tuning", "LLM Evaluation", "Multi-Modal Integration",
    "AutoGen", "CrewAI", "LangChain", "Chain-of-Thought (CoT)", "LoRA", "QLoRA", "PEFT", "Ragas", "Hugging Face",
    "GCP", "Azure", "AWS",
    "Python", "Java", "Spring Boot", "Node.js",
    "Databricks", "Snowflake", "BigQuery", "PostgreSQL", "MySQL",
    "Angular", "React", "Vue.js", "TypeScript", "HTML", "CSS",
    "Agile Methodologies", "Planning & Scheduling", "Communication & Leadership"
  ],
  "experience": [
    {
      "title": "Data Architecture Associate Manager",
      "company": "Accenture Japan",
      "location": "Tokyo, Japan",
      "start_date": "January 2021",
      "end_date": "Present",
      "roles": [
        {
          "title": "Gen AI Architect",
          "description": "Designed and deployed AI solutions using agentic architecture, RAG, and LLM fine-tuning for chatbots and automation. Achieved a 40% cost reduction in legacy code modernization."
        },
        {
          "title": "Cloud Solution AI Architect",
          "description": "Built cloud infrastructures in Azure and GCP, integrating AI for chatbot applications and optimized delivery routes using GCP's AI Optimization."
        },
        {
          "title": "Project Manager",
          "description": "Managed 3+ global teams to deliver AI-powered solutions with effective collaboration, system design communication, and timely execution."
        },
        {
          "title": "Full-Stack Developer",
          "description": "Developed APIs, database structures, and web features to ensure high-performance, scalable systems."
        }
      ]
    }
  ],
  "projects": [
    {
      "name": "Bank Buddy AI Agent",
      "start_date": "February 2024",
      "end_date": "February 2025",
      "description": "Automated 85% of back-office banking tasks using Autogen architecture. Integrated OCR for eKYC verification and deployed agent swarms for real-time performance dashboards."
    },
    {
      "name": "Legacy Code Modernization",
      "start_date": "June 2023",
      "end_date": "March 2024",
      "description": "Modernized legacy COBOL systems to Java using AI-powered tools, reducing review time by 40% and cutting operational costs by 25% through containerization."
    },
    {
      "name": "Optimized Delivery Route Application",
      "start_date": "February 2021",
      "end_date": "July 2023",
      "description": "Developed logistics optimization app using GCP AI, reducing delivery time by 25%. Fine-tuned a Japanese BERT model on 500k+ addresses to improve address handling."
    }
  ],
  "education": {
    "degree": "Bachelor of Technology in Electrical Engineering",
    "institution": "Indian Institute of Technology, Kharagpur",
    "location": "West Bengal, India",
    "start_date": "July 2016",
    "end_date": "July 2020"
  }
}

✅ Success Criteria
Application is fully submitted via Easy Apply (or marked for manual review if not possible).

Fields are filled accurately and professionally.

Resume is uploaded when applicable.

Confirmation or tracking data is logged.

⚠️ Notes
Do not apply to duplicate jobs.

Avoid roles clearly outside of skill set (e.g., senior if user is entry-level).

Skip if application involves third-party sites with captcha or complex authentication.


"""
apath="/Users/anand/Downloads/AI anand's cv.docx"
async def main():
    # If no executable_path provided, uses Playwright/Patchright's built-in Chromium
    user_data_dir="/Users/anand/Library/Application Support/Google/Chrome/Default"
    # with async_playwright() as p:
    #     browser = p.chromium.  l. aunch_persistent_context(
    #         user_data_dir=user_data_dir,
    #         headless=False)
    browser_session = BrowserSession(
      #  user_data_dir=user_data_dir,
      #  browser_context=browser,
    # Path to a specific Chromium-based executable (optional)
    #executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
    # For Windows: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    # For Linux: '/usr/bin/google-chrome'
    
    # Use a specific data directory on disk (optional, set to None for incognito)
    #user_data_dir=  None,   # this is the default
    # ... any other BrowserProfile or playwright launch_persistnet_context config...
    # headless=False,
    )

    agent = Agent(
        task="open linkedin and apply this job https://www.linkedin.com/jobs/view/manager-machine-learning-engineering-at-hca-healthcare-4256329096",
        llm=llm,
        browser_session=browser_session,
        extend_system_message=extend_system_message,
        available_file_paths=[apath],  # List of file paths to be used in the agent
        controller=controller
    )

    result = await agent.run()
    print(result)

asyncio.run(main())



# from openai import OpenAI

# client = OpenAI()

# response = client.responses.create(
#   model="gpt-4o",
#   input="Tell me a three sentence bedtime story about a unicorn."
# )

# print(response)
