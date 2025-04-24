from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("API_KEY")

# Configure Gemini Client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")


def extract_text_from_pdf(file) -> str:
    pdf = fitz.open(stream=file.file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text


@app.post("/parse_resume")
async def parse_resume(file: UploadFile = File(...), fields: str = Form(...)):
    try:
        text = extract_text_from_pdf(file)
        prompt = f"Extract the following details from this resume: {fields}. Separate each field clearly in the format `Field: value`. Do not use any markdown, bullet points, or unnecessary formatting. Resume content:\n\n{text}"

        response = model.generate_content(prompt)

        return {"parsed_data": response.text}
    except Exception as e:
        return {"error": str(e)}

