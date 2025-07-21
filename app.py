import streamlit as st
import os
from openai import OpenAI
from docx import Document
from fpdf import FPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set Streamlit page config
st.set_page_config(page_title="API Contract Generator", layout="wide")
st.title("📄 AI-Powered API Contract Generator")
st.markdown("Fill in the API metadata below and click **Generate Contract** to create a complete API documentation.")

# Form inputs
with st.form("contract_form"):
    api_name = st.text_input("API Name", value="Task Management API")
    version = st.text_input("Version", value="v1.0.0")
    base_url = st.text_input("Base URL", value="https://api.taskhub.com/v1")
    auth_method = st.selectbox("Authentication Method", ["JWT Bearer", "API Key", "Basic Auth"])
    content_type = st.text_input("Content-Type", value="application/json")
    response_format = st.text_input("Response Format", value="application/json")
    auth_header_example = st.text_input("Example Authorization Header", value="Authorization: Bearer <token>")
    global_headers = st.text_area("Global Headers", value="- Authorization: string (required) - JWT access token\n- Content-Type: string (required) - MIME type")
    entities = st.text_area("Entities", value="- Task: title, description, dueDate, priority, status\n- Project: name, description, owner\n- User: name, email, role")
    endpoints = st.text_area("Endpoints", value="""
- POST `/tasks` - Create a new task
- GET `/tasks/{id}` - Get task by ID
- PUT `/tasks/{id}` - Update a task
- DELETE `/tasks/{id}` - Delete a task
- GET `/projects` - List all projects
- POST `/users/login` - Login and get token
""")
    submit = st.form_submit_button("🚀 Generate Contract")

# Build prompt
def build_prompt(api_name, version, base_url, auth_method, content_type, response_format,
                 auth_header_example, global_headers, entities, endpoints):
    return f"""
You are an expert technical writer and backend architect. I need you to generate a complete API contract documentation for a RESTful API, following the structure and level of detail used by professional API teams.

Generate the API documentation in the following format:

---

1. **API Overview**
   - API Name: {api_name}
   - Version: {version}
   - Base URL: {base_url}
   - Authentication method: {auth_method}
   - Content-Type: {content_type}
   - Response Format: {response_format}

2. **Authentication**
   - Type: {auth_method}
   - Example Authorization Header: {auth_header_example}

3. **Global Headers**
Include a table of common headers required across all endpoints
{global_headers}

4. **Error Handling**
   - List common HTTP status codes (e.g., 400, 401, 403, 404, 500)
   - Include common HTTP status codes
   - Standard error JSON structure

5. **Endpoints**
   Based on the following definitions:
{endpoints}
For example each endpoint can include based on the need:

Method: GET / POST / PUT / DELETE

Endpoint URL

Description

Path Parameters (if any)

Query Parameters (if any)

Headers (if specific to endpoint)

Request Body

JSON Schema or field-level description

Example request in JSON

Response Body

JSON Schema or field-level description

Example response in JSON

Success HTTP Status Code(s)

Error HTTP Status Codes

Notes (if any)

6. **Data Types**
   - Provide a table describing custom object types, enums, and field descriptions
   - Use a table to describe types

7. **Rate Limiting**
Maximum requests per minute/hour

Rate limiting headers to be monitored
   - Requests per minute/hour
   - Rate limit headers

8. **Changelog**
   Example:

   v1.0.0 – Initial release with basic CRUD endpoints
   

9. **Appendix**
   - Security considerations
   - Environment URLs (e.g., Production, Staging)

10. **Contact & Support**
    - Add dummy email and repo link

---

**Main Entities**:
{entities}

Use Markdown formatting and professional tone.
Include JSON examples and tables where needed.
"""

# PDF & DOCX generation
def generate_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 10, txt=safe_line)
    output_path = os.path.join("/mnt/data", filename)
    pdf.output(output_path)
    return output_path

def generate_docx(text, filename):
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    output_path = os.path.join("/mnt/data", filename)
    doc.save(output_path)
    return output_path

# Process form submission
if submit:
    with st.spinner("Generating API Contract..."):
        prompt = build_prompt(api_name, version, base_url, auth_method, content_type,
                              response_format, auth_header_example, global_headers, entities, endpoints)
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            contract_text = response.choices[0].message.content.strip()
            st.success("✅ Contract generated successfully!")
            st.markdown("### 📘 API Documentation Preview")
            st.markdown(contract_text)

            #pdf_file = generate_pdf(contract_text, "api_contract.pdf")
            #docx_file = generate_docx(contract_text, "api_contract.docx")

            #st.download_button("⬇️ Download as PDF", data=open(pdf_file, "rb"), file_name="api_contract.pdf")
            #st.download_button("⬇️ Download as Word", data=open(docx_file, "rb"), file_name="api_contract.docx")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
