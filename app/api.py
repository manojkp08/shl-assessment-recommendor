# # api.py:

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import chromadb
# from bs4 import BeautifulSoup
# import requests
# from fastapi.middleware.cors import CORSMiddleware
# import cohere
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# # Initialize Cohere (free tier)
# try:
#     co = cohere.Client(os.getenv("COHERE_API_KEY"))  # Free API key
# except:
#     co = None

# app = FastAPI()

# chroma_client = chromadb.PersistentClient(path="app/chroma_db")

# class QueryRequest(BaseModel):
#     text: str  # Can be a prompt OR job URL
#     use_ai: bool = True  # Toggle for AI insights

# def scrape_job_description(url: str) -> str:
#     """Scrape job description from URL (SHL-style pages)"""
#     try:
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=50)
#         soup = BeautifulSoup(response.text, "html.parser")
#         job_desc_div = soup.select_one("div.job-description, section.description")
#         return job_desc_div.get_text(" ", strip=True) if job_desc_div else ""
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Scraping error: {str(e)}")
    
# def normalize_score(score: float) -> float:
#     """Ensure scores are between 0-1 with fallback"""
#     try:
#         return max(0.0, min(1.0, abs(float(score))))  # Force 0-1 range
#     except:
#         return 0.5  # Default neutral score

# def generate_cohere_insights(name: str, description: str) -> str:
#     """Generate short HR-focused insights"""
#     if not co:
#         return "AI insights unavailable"
    
#     try:
#         prompt = f"""As an HR expert, analyze this SHL assessment and respond in exactly 3 short lines:
        
#         Assessment Name: {name}
#         Description: {description[:300]}  # Shortened to reduce token usage
        
#         Format your response as:
#         1. Key skills: [very brief, 4-5 words only]
#         2. Job level fit: [very brief, 2-3 words only]  
#         3. Usage tip: [very brief, 4-5 words only]"""
        
#         response = co.generate(
#             model='command',  # Free model
#             prompt=prompt,
#             max_tokens=50,  # Reduced token count
#             temperature=0.5  # Lower temperature for more consistent responses
#         )
#         return response.generations[0].text
#     except Exception as e:
#         return "AI insights unavailable (limit reached)"


# @app.post("/recommend")
# async def recommend(request: QueryRequest):
#     try:
#         collection = chroma_client.get_collection("shl_assessments")
#     except ValueError:
#         raise HTTPException(status_code=500, detail="Vector DB not initialized")

#     # Handle URL or text query
#     query_text = request.text
#     if query_text.startswith(("http://", "https://")):
#         query_text = scrape_job_description(query_text)

#     # Semantic search
#     results = collection.query(
#         query_texts=[query_text],
#         n_results=10
#     )

#     # Build response
#     recommendations = []
#     for i in range(len(results["ids"][0])):
#         raw_score = float(results["distances"][0][i])
#         item = {
#             "name": results["metadatas"][0][i]["name"],
#             "url": results["metadatas"][0][i]["url"],
#             "score": normalize_score(raw_score),
#             "ai_insights": ""
#         }
        
#         if request.use_ai:
#             item["ai_insights"] = generate_cohere_insights(
#                 item["name"],
#                 results["metadatas"][0][i]["description"]
#             )
        
#         recommendations.append(item)

#     return recommendations


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from bs4 import BeautifulSoup
import requests
from fastapi.middleware.cors import CORSMiddleware
import cohere
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Cohere (free tier)
try:
    co = cohere.Client(os.getenv("COHERE_API_KEY"))
except:
    co = None

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma_client = chromadb.PersistentClient(path="app/chroma_db")

class QueryRequest(BaseModel):
    text: str
    use_ai: bool = True

def scrape_job_description(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=50)
        soup = BeautifulSoup(response.text, "html.parser")
        job_desc_div = soup.select_one("div.job-description, section.description")
        return job_desc_div.get_text(" ", strip=True) if job_desc_div else ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scraping error: {str(e)}")
    
def normalize_score(score: float) -> float:
    try:
        return max(0.0, min(1.0, abs(float(score))))
    except:
        return 0.5

def generate_cohere_insights(description: str) -> str:
    if not co:
        return "AI insights unavailable"
    
    try:
        prompt = f"""As an HR expert, analyze this assessment description and provide 3 concise insights:
        
        Description: {description[:300]}
        
        Format as:
        1. Key skills measured
        2. Ideal candidate level
        3. Best use case"""
        
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=50,
            temperature=0.5
        )
        return response.generations[0].text
    except Exception as e:
        return "AI insights unavailable"

@app.post("/recommend")
async def recommend(request: QueryRequest):
    try:
        collection = chroma_client.get_collection("shl_assessments")
    except ValueError:
        raise HTTPException(status_code=500, detail="Vector DB not initialized")

    query_text = request.text
    if query_text.startswith(("http://", "https://")):
        query_text = scrape_job_description(query_text)

    results = collection.query(
        query_texts=[query_text],
        n_results=10,
        include=["metadatas", "documents", "distances"]
    )

    recommendations = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        recommendations.append({
            "name": metadata["name"],
            "url": metadata["url"],
            "description": metadata["description"],
            "duration": metadata.get("duration", "Not specified"),
            "languages": metadata.get("languages", []),
            "job_level": metadata.get("job_level", "Not specified"),
            "remote_testing": metadata.get("remote_testing", "❓"),
            "adaptive_support": metadata.get("adaptive/irt_support", "❓"),
            "test_type": metadata.get("test_type", "Not specified"),
            "score": normalize_score(results["distances"][0][i]),
            "ai_insights": generate_cohere_insights(metadata["description"]) if request.use_ai else ""
        })

    return recommendations