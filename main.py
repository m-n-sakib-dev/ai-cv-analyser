from fastapi import FastAPI, HTTPException, Form , Body
from typing import List
from dotenv import load_dotenv
from google import genai
import os
import fitz
import json
import re
import pprint

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Ai cv analyzer is running"}

@app.post("/analyze-cv")
def analyze_cv(file_path: str = Body(...), position: str = Body(...)):
    print(file_path)
    if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found at given path")

    if not file_path.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    rating=analyze_cv_byAi(file_path,position)
    pprint.pprint(rating)
    return{
        "data":rating
    }

@app.post("/sort-cv")
def upload_cv(file_paths: List[str] = Form(...), position:str =Form(...)):
    rating=[]
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found at given path")

        if not file_path.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        rating.append(analyze_cv_byAi(file_path,position))
    print(rating)
    sorted_rating = sorted(rating, key=lambda x: float(x['rating']), reverse=True)
    print(sorted_rating)
    return{
        "data":sorted_rating
    }
   



def analyze_cv_byAi(file_path:str, position:str):
        pdf = fitz.open(file_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        prompt = f"""Analyze the following CV and give a rating out of 10 for the position of {position}.

                            Provide:
                             Overall Rating (out of 10)
                            
                            dont give any extra text out of that. give response in float formate like  8.5
                            CV Content:
                            {text}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(response.text)
        # clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        # data = json.loads(clean_json)
        return {
            "file_path": file_path,
            "rating": response.text
        }